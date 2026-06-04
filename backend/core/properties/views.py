from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import secrets
import threading
import logging
import json
import requests
import os
from .models import Locality, Property, PropertyImage, PropertyHistory, Chat, ChatMessage
from .serializers import LocalitySerializer, PropertySerializer, PropertyImageSerializer, PropertyHistorySerializer, ChatSerializer, ChatMessageSerializer
from .tasks import enrich_locality_pipeline

logger = logging.getLogger(__name__)

class LocalityViewSet(viewsets.ModelViewSet):
    queryset = Locality.objects.all().select_related('profile')
    serializer_class = LocalitySerializer

    def create(self, request, *args, **kwargs):
        lat = request.data.get('latitude')
        lng = request.data.get('longitude')
        name = request.data.get('name')
        city = request.data.get('city')

        if not lat or not lng or not name or not city:
            return Response({"error": "Missing mandatory field records."}, status=status.HTTP_400_BAD_REQUEST)

        locality, created = Locality.objects.get_or_create(
            latitude=lat,
            longitude=lng,
            defaults={'name': name, 'city': city}
        )

        if created:
            print(f"✓ New locality created: {locality.id} ({name}, {city})")
            # Run AI enrichment in background thread (non-blocking)
            thread = threading.Thread(target=enrich_locality_pipeline, args=(locality.id,), daemon=True)
            thread.start()
            print(f"✓ Background thread started for AI analysis of locality {locality.id}")

        serializer = self.get_serializer(locality)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def enrich(self, request, pk=None):
        """Trigger AI enrichment for a locality"""
        locality = self.get_object()
        
        if locality.profile:
            return Response({
                "status": "already_enriched",
                "message": f"Locality '{locality.name}' already has analysis"
            })
        
        try:
            # Run AI enrichment in background thread
            thread = threading.Thread(target=enrich_locality_pipeline, args=(locality.id,), daemon=True)
            thread.start()
            return Response({
                "status": "processing",
                "message": f"AI analysis started for '{locality.name}'. Will complete in 2-5 minutes."
            })
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'])
    def properties(self, request, pk=None):
        locality = self.get_object()
        properties = Property.objects.filter(locality=locality)
        serializer = PropertySerializer(properties, many=True)
        return Response(serializer.data)

class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer


class PropertyImageViewSet(viewsets.ModelViewSet):
    queryset = PropertyImage.objects.all()
    serializer_class = PropertyImageSerializer
    
    @action(detail=False, methods=['get'])
    def by_property(self, request):
        """Get all images for a specific property"""
        property_id = request.query_params.get('property_id')
        if not property_id:
            return Response({'error': 'property_id parameter required'}, status=status.HTTP_400_BAD_REQUEST)
        
        images = PropertyImage.objects.filter(property_id=property_id)
        serializer = self.get_serializer(images, many=True)
        return Response(serializer.data)


class PropertyHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PropertyHistory.objects.all()
    serializer_class = PropertyHistorySerializer
    
    @action(detail=False, methods=['get'])
    def by_property(self, request):
        """Get all history for a specific property"""
        property_id = request.query_params.get('property_id')
        if not property_id:
            return Response({'error': 'property_id parameter required'}, status=status.HTTP_400_BAD_REQUEST)
        
        history = PropertyHistory.objects.filter(property_id=property_id)
        serializer = self.get_serializer(history, many=True)
        return Response(serializer.data)


class ChatViewSet(viewsets.ModelViewSet):
    serializer_class = ChatSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """Authenticated users see their chats; anonymous users need a token on detail actions."""
        user = self.request.user
        if user.is_authenticated:
            if user.is_superuser:
                return Chat.objects.all()
            return (Chat.objects.filter(user=user) | Chat.objects.filter(admin=user)).distinct()
        return Chat.objects.none()

    def get_visitor_token(self, request):
        return request.data.get('visitor_token') or request.query_params.get('visitor_token')

    def user_can_access_chat(self, request, chat):
        user = request.user
        if user.is_authenticated and (
            user.is_superuser or chat.user_id == user.id or chat.admin_id == user.id
        ):
            return True

        visitor_token = self.get_visitor_token(request)
        if visitor_token and chat.visitor_token:
            return secrets.compare_digest(str(visitor_token), str(chat.visitor_token))

        return False

    def get_chat_by_pk(self, pk):
        try:
            return Chat.objects.get(pk=pk)
        except Chat.DoesNotExist:
            return None

    def retrieve(self, request, *args, **kwargs):
        chat = self.get_chat_by_pk(kwargs.get('pk'))
        if not chat:
            return Response({'error': 'Chat not found'}, status=status.HTTP_404_NOT_FOUND)

        if not self.user_can_access_chat(request, chat):
            return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(chat)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """Create a new chat for a property when user is interested"""
        property_id = request.data.get('property')
        
        if not property_id:
            return Response({'error': 'property id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            property_obj = Property.objects.get(id=property_id)
        except Property.DoesNotExist:
            return Response({'error': 'Property not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get visitor info from request
        visitor_name = request.data.get('visitor_name')
        visitor_email = request.data.get('visitor_email')
        visitor_phone = request.data.get('visitor_phone')
        
        # Create chat with visitor info (anonymous or authenticated user)
        user = request.user if request.user.is_authenticated else None
        
        chat = Chat.objects.create(
            user=user,
            property=property_obj,
            visitor_name=visitor_name,
            visitor_email=visitor_email,
            visitor_phone=visitor_phone,
            is_active=True
        )
        
        serializer = self.get_serializer(chat)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """Send a message in a chat"""
        try:
            print(f"DEBUG: send_message called with pk={pk}")
            chat = self.get_chat_by_pk(pk)
            if not chat:
                return Response({'error': 'Chat not found'}, status=status.HTTP_404_NOT_FOUND)
            if not self.user_can_access_chat(request, chat):
                return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
            print(f"DEBUG: Got chat: {chat.id}")
            
            message_text = request.data.get('message')
            print(f"DEBUG: message_text={message_text}")
            
            if not message_text or not message_text.strip():
                return Response({'error': 'message required'}, status=status.HTTP_400_BAD_REQUEST)
            
            # For anonymous users, create or use a temporary user associated with the chat
            from django.contrib.auth.models import User
            from uuid import uuid4
            
            if request.user.is_authenticated:
                sender = request.user
                print(f"DEBUG: Using authenticated user {sender}")
            else:
                # Create temporary user for anonymous chat if needed
                if not chat.user:
                    # Try to get or create a temp user for this visitor
                    temp_username = f"visitor_{uuid4().hex[:8]}"
                    sender, _ = User.objects.get_or_create(
                        username=temp_username,
                        defaults={'email': chat.visitor_email or '', 'first_name': chat.visitor_name or 'Visitor'}
                    )
                    print(f"DEBUG: Created temp user {sender}")
                    # Link to chat so subsequent messages use same user
                    if not chat.user:
                        chat.user = sender
                        chat.save()
                else:
                    sender = chat.user
                    print(f"DEBUG: Using existing chat user {sender}")
            
            message = ChatMessage.objects.create(
                chat=chat,
                sender=sender,
                message=message_text.strip()
            )
            print(f"DEBUG: Message created: {message.id}")
            
            serializer = ChatMessageSerializer(message)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(f"ERROR in send_message: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get all messages in a chat"""
        chat = self.get_chat_by_pk(pk)
        if not chat:
            return Response({'error': 'Chat not found'}, status=status.HTTP_404_NOT_FOUND)
        if not self.user_can_access_chat(request, chat):
            return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)

        messages = chat.messages.all()
        
        # Mark all unread messages as read for the current user
        if request.user == chat.admin:
            ChatMessage.objects.filter(chat=chat, is_read=False).exclude(sender=request.user).update(is_read=True)
        
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def assign_admin(self, request, pk=None):
        """Assign an admin to handle the chat"""
        chat = self.get_object()
        admin_id = request.data.get('admin_id')
        
        if not admin_id:
            return Response({'error': 'admin_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from django.contrib.auth.models import User
            admin = User.objects.get(id=admin_id, is_staff=True)
        except User.DoesNotExist:
            return Response({'error': 'Admin user not found'}, status=status.HTTP_404_NOT_FOUND)
        
        chat.admin = admin
        chat.save()
        
        serializer = self.get_serializer(chat)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """Close a chat"""
        chat = self.get_object()
        chat.is_active = False
        chat.save()
        
        serializer = self.get_serializer(chat)
        return Response(serializer.data)


# ==================== AUTOCOMPLETE & COORDINATE VIEWS ====================

@require_http_methods(["GET"])
@csrf_exempt
def autocomplete_location(request):
    """
    Autocomplete endpoint for location search
    Uses SerpAPI to find locations matching the query and city
    
    Query Parameters:
    - q: Search query (sector name, landmark, etc.)
    - city: City filter (required)
    
    Returns JSON with matching locations and their coordinates
    """
    # Rate limiting disabled - removed as per request
    
    query = request.GET.get('q', '').strip()
    city = request.GET.get('city', '').strip()
    
    # Validation
    if not query or len(query) < 2:
        return JsonResponse({
            'results': [],
            'message': 'Query too short (minimum 2 characters)',
            'api_status': 'user_input'
        })
    
    if not city:
        return JsonResponse({
            'error': 'City parameter is required',
            'api_status': 'user_input'
        }, status=400)
    
    serp_key = os.getenv('SERPAPI_API_KEY')
    if not serp_key:
        return JsonResponse({
            'results': [],
            'error': 'API not configured',
            'api_status': 'api_down',
            'message': 'SerpAPI key not configured. Please manually enter coordinates.'
        }, status=503)
    
    try:
        # Search for locations using SerpAPI
        serp_url = "https://serpapi.com/search.json"
        params = {
            "engine": "google_maps",
            "q": f"{query} {city}",
            "type": "search",
            "api_key": serp_key
        }
        
        response = requests.get(serp_url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract location results - try multiple response formats from SerpAPI
        results = []
        
        # Try local_results first (most common)
        local_results = data.get('local_results', [])
        
        # If empty, try places results
        if not local_results:
            local_results = data.get('places', [])
        
        # If still empty, try knowledge_graph locations
        if not local_results and data.get('knowledge_graph'):
            kg = data.get('knowledge_graph', {})
            if kg.get('type') == 'Place':
                local_results = [kg]
        
        logger.info(f"SerpAPI response - local_results: {len(local_results)}, places: {len(data.get('places', []))}")
        
        # Parse results with flexible field mapping
        for item in local_results[:10]:  # Limit to 10 results
            # Handle different SerpAPI response formats
            name = item.get('title') or item.get('name') or item.get('place_name') or ''
            address = item.get('address') or item.get('formatted_address') or ''
            lat = item.get('latitude') or item.get('lat')
            lng = item.get('longitude') or item.get('lng')

            # Handle nested coordinate formats from SerpAPI
            if lat is None or lng is None:
                gps = item.get('gps_coordinates') or item.get('gps') or {}
                if isinstance(gps, dict):
                    lat = lat if lat is not None else gps.get('latitude') or gps.get('lat')
                    lng = lng if lng is not None else gps.get('longitude') or gps.get('lng')

            if lat is None or lng is None:
                geometry = item.get('geometry') or {}
                if isinstance(geometry, dict):
                    location = geometry.get('location') or {}
                    if isinstance(location, dict):
                        lat = lat if lat is not None else location.get('lat')
                        lng = lng if lng is not None else location.get('lng')
            place_id = item.get('place_id') or item.get('id') or ''
            
            # Convert to float if string
            try:
                if isinstance(lat, str):
                    lat = float(lat)
                if isinstance(lng, str):
                    lng = float(lng)
            except (ValueError, TypeError):
                lat = None
                lng = None
            
            result = {
                'id': place_id,
                'name': name,
                'address': address,
                'latitude': lat,
                'longitude': lng,
                'type': item.get('type', 'location')
            }
            
            # Only include results with valid data
            if name and lat is not None and lng is not None:
                results.append(result)
        
        logger.info(f"Autocomplete: query='{query}', city='{city}', final_results={len(results)}")
        
        return JsonResponse({
            'results': results,
            'api_status': 'success',
            'query': query,
            'city': city,
            'count': len(results)
        })
    
    except requests.exceptions.Timeout:
        logger.warning(f"SerpAPI timeout for query: {query}")
        return JsonResponse({
            'results': [],
            'error': 'Request timeout',
            'api_status': 'api_down',
            'message': 'Location search is taking too long. Please manually enter coordinates.'
        }, status=503)
    
    except requests.exceptions.RequestException as e:
        logger.error(f"SerpAPI error: {str(e)}")
        return JsonResponse({
            'results': [],
            'error': 'API error',
            'api_status': 'api_down',
            'message': 'Location service is temporarily unavailable. Please manually enter coordinates.'
        }, status=503)
    
    except Exception as e:
        logger.error(f"Unexpected error in autocomplete: {str(e)}")
        return JsonResponse({
            'results': [],
            'error': 'Unexpected error',
            'api_status': 'error',
            'message': 'An unexpected error occurred. Please manually enter coordinates.'
        }, status=500)


@require_http_methods(["GET"])
@csrf_exempt
def get_coordinates(request):
    """
    Get coordinates for a specific location
    Used when autocomplete result is selected
    
    Query Parameters:
    - location: Location name or address
    - city: City name (for context)
    
    Returns JSON with latitude and longitude
    """
    # Rate limiting disabled - removed as per request
    
    location = request.GET.get('location', '').strip()
    city = request.GET.get('city', '').strip()
    
    if not location or not city:
        return JsonResponse({
            'error': 'Location and city parameters required',
            'api_status': 'user_input'
        }, status=400)
    
    serp_key = os.getenv('SERPAPI_API_KEY')
    if not serp_key:
        return JsonResponse({
            'error': 'API not configured',
            'api_status': 'api_down'
        }, status=503)
    
    try:
        serp_url = "https://serpapi.com/search.json"
        params = {
            "engine": "google_maps",
            "q": f"{location} {city}",
            "type": "search",
            "api_key": serp_key
        }
        
        response = requests.get(serp_url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        local_results = data.get('local_results', [])
        
        if local_results:
            first_result = local_results[0]
            return JsonResponse({
                'latitude': first_result.get('latitude'),
                'longitude': first_result.get('longitude'),
                'name': first_result.get('title', ''),
                'address': first_result.get('address', ''),
                'api_status': 'success'
            })
        else:
            return JsonResponse({
                'error': 'Location not found',
                'api_status': 'not_found'
            }, status=404)
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching coordinates: {str(e)}")
        return JsonResponse({
            'error': 'API error',
            'api_status': 'api_down'
        }, status=503)
    
    except Exception as e:
        logger.error(f"Unexpected error in get_coordinates: {str(e)}")
        return JsonResponse({
            'error': 'Unexpected error',
            'api_status': 'error'
        }, status=500)
