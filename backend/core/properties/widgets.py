"""
Custom Django widgets for location autocomplete in admin
Includes LocationAutocompleteWidget with integrated coordinate fetching
"""

from django import forms
from django.utils.safestring import mark_safe
import json


class LocationAutocompleteWidget(forms.TextInput):
    """
    Custom widget for location autocomplete with coordinate auto-fill
    
    Features:
    - Real-time autocomplete suggestions from SerpAPI
    - Auto-fill latitude/longitude on selection
    - Fallback to manual entry when API is down
    - City filtering
    """
    
    def __init__(self, city_field_name='city', attrs=None):
        """
        Initialize widget
        
        Args:
            city_field_name: Name of the city field in the form (for filtering)
            attrs: HTML attributes
        """
        super().__init__(attrs or {})
        self.city_field_name = city_field_name
        self.attrs['autocomplete'] = 'off'
        self.attrs['class'] = 'location-autocomplete-input'
        self.attrs['placeholder'] = 'Start typing sector name, landmark, or area...'
    
    def render(self, name, value, attrs=None, renderer=None):
        """Render the widget with autocomplete HTML and JavaScript"""
        
        final_attrs = self.build_attrs(attrs or {}, {'name': name})
        final_attrs['id'] = final_attrs.get('id', f'id_{name}')
        final_attrs['autocomplete'] = 'off'
        final_attrs['class'] = 'location-autocomplete-input'
        final_attrs['placeholder'] = 'Start typing sector name, landmark, or area...'
        
        # Build HTML attributes string safely
        attrs_parts = []
        for k, v in final_attrs.items():
            if v is not None:
                # Escape attribute values
                v_str = str(v).replace('"', '&quot;')
                attrs_parts.append(f'{k}="{v_str}"')
        attrs_str = ' '.join(attrs_parts)
        
        # City field name (resolved in JS with form prefix)
        city_field_name = self.city_field_name
        
        # Render HTML inline
        html = f'''<div class="location-autocomplete-container">
    <input {attrs_str} value="{value or ''}" />
</div>'''
        
        # Add CSS and JavaScript
        js_html = self._render_js(final_attrs['id'], city_field_name)
        
        return mark_safe(html + js_html)
    
    def _render_js(self, input_id, city_field_name):
        """Generate JavaScript for autocomplete functionality"""
        
        js_code = f"""
        <style>
            .location-autocomplete-container {{
                position: relative;
                width: 100%;
                max-width: 520px;
            }}
            
            .location-autocomplete-dropdown {{
                position: fixed !important;
                top: auto;
                left: auto;
                width: min(520px, calc(100vw - 32px));
                margin: 0;
                background: #ffffff;
                border: 1px solid #c7cdd3;
                border-radius: 4px;
                display: block !important;
                height: auto !important;
                min-height: 48px;
                max-height: min(320px, calc(100vh - 32px));
                overflow-x: hidden;
                overflow-y: auto !important;
                z-index: 1100 !important;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.18);
            }}
            
            .location-autocomplete-item {{
                display: block;
                padding: 10px 12px;
                border-bottom: 1px solid #edf0f2;
                cursor: pointer;
                box-sizing: border-box;
                height: auto !important;
                min-height: 44px;
                color: #202124 !important;
                line-height: 1.35;
                transition: background-color 0.15s ease;
            }}

            .location-autocomplete-item:last-child {{
                border-bottom: 0;
            }}
            
            .location-autocomplete-item:hover {{
                background-color: #f1f5f9;
            }}
            
            .location-autocomplete-item-name {{
                display: block;
                font-weight: 600;
                color: #202124;
                white-space: normal;
                overflow-wrap: anywhere;
            }}
            
            .location-autocomplete-item-address {{
                display: block;
                margin-top: 3px;
                color: #5f6368;
                font-size: 12px;
                white-space: normal;
                overflow-wrap: anywhere;
            }}
            
            .api-status-message {{
                display: inline-block;
                max-width: 100%;
                box-sizing: border-box;
                padding: 6px 9px;
                margin-top: 6px;
                border-radius: 4px;
                font-size: 12px;
            }}
            
            .api-status-message.error {{
                background-color: #fee;
                color: #c33;
                border: 1px solid #fcc;
            }}
            
            .api-status-message.warning {{
                background-color: #ffeaa7;
                color: #856404;
                border: 1px solid #ffeaa7;
            }}
            
            .api-status-message.success {{
                background-color: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }}
            
            .manual-entry-notice {{
                padding: 8px;
                background-color: #fff3cd;
                border: 1px solid #ffc107;
                border-radius: 4px;
                margin-top: 8px;
                font-size: 0.85em;
                color: #856404;
            }}
            
            .coordinates-display {{
                padding: 8px;
                background-color: #e8f4f8;
                border: 1px solid #b3d9e8;
                border-radius: 4px;
                margin-top: 8px;
                font-size: 0.85em;
                color: #2c3e50;
            }}

            @media (max-width: 600px) {{
                .location-autocomplete-dropdown {{
                    width: calc(100vw - 32px);
                }}
            }}
        </style>
        
        <script>
        (function() {{
            // Initialize after a short delay to ensure DOM is ready
            setTimeout(function() {{
                try {{
                    const inputId = '{input_id}';
                    const cityFieldName = '{city_field_name}';
                    
                    const inputElement = document.getElementById(inputId);
                    if (!inputElement) {{
                        console.warn('[Autocomplete] Input element not found: ' + inputId);
                        return;
                    }}
                    
                    console.log('[Autocomplete] Initializing for element: ' + inputId);
                    
                    // Create container if needed
                    let container = inputElement.parentElement;
                    if (!container.classList.contains('location-autocomplete-container')) {{
                        container = document.createElement('div');
                        container.className = 'location-autocomplete-container';
                        inputElement.parentElement.insertBefore(container, inputElement);
                        container.appendChild(inputElement);
                    }}
                    
                    // Create dropdown
                    let dropdown = null;
                    let isOpen = false;
                    let results = [];
                    
                    // Add status message div if not exists
                    let statusDiv = document.getElementById('location-status-message-' + inputId);
                    if (!statusDiv) {{
                        statusDiv = document.createElement('div');
                        statusDiv.id = 'location-status-message-' + inputId;
                        container.appendChild(statusDiv);
                    }}
                    
                    function showStatus(message, type) {{
                        statusDiv.innerHTML = '<div class="api-status-message ' + type + '">' + message + '</div>';
                        console.log('[Autocomplete] ' + type.toUpperCase() + ': ' + message);
                    }}
                    
                    function clearStatus() {{
                        statusDiv.innerHTML = '';
                    }}
                    
                    function createDropdown(items) {{
                        // Remove old dropdown
                        if (dropdown) dropdown.remove();
                        
                        dropdown = document.createElement('div');
                        dropdown.className = 'location-autocomplete-dropdown';
                        
                        if (items.length === 0) {{
                            dropdown.innerHTML = '<div class="location-autocomplete-item">No results found</div>';
                        }} else {{
                            items.forEach(function(item) {{
                                const div = document.createElement('div');
                                div.className = 'location-autocomplete-item';
                                div.innerHTML = '<div class="location-autocomplete-item-name">' + 
                                    (item.name || 'Unknown') + 
                                    '</div><div class="location-autocomplete-item-address">' + 
                                    (item.address || '') + '</div>';
                                
                                div.addEventListener('click', function(e) {{
                                    e.preventDefault();
                                    e.stopPropagation();
                                    selectItem(item);
                                }});
                                
                                dropdown.appendChild(div);
                            }});
                        }}
                        
                        container.appendChild(dropdown);
                        positionDropdown();
                        isOpen = true;
                        console.log('[Autocomplete] Dropdown shown with ' + items.length + ' items');
                    }}

                    function positionDropdown() {{
                        if (!dropdown) return;

                        const inputRect = inputElement.getBoundingClientRect();
                        const viewportPadding = 16;
                        const availableWidth = window.innerWidth - inputRect.left - viewportPadding;
                        const dropdownWidth = Math.min(520, Math.max(inputRect.width, 280), availableWidth);
                        const availableHeight = window.innerHeight - inputRect.bottom - viewportPadding;

                        dropdown.style.left = Math.max(viewportPadding, inputRect.left) + 'px';
                        dropdown.style.top = (inputRect.bottom + 4) + 'px';
                        dropdown.style.width = Math.max(280, dropdownWidth) + 'px';
                        dropdown.style.maxHeight = Math.max(120, Math.min(320, availableHeight)) + 'px';
                    }}
                    
                    function hideDropdown() {{
                        if (dropdown) {{
                            dropdown.remove();
                            dropdown = null;
                            isOpen = false;
                        }}
                    }}
                    
                    function selectItem(item) {{
                        inputElement.value = item.name || '';
                        hideDropdown();
                        clearStatus();
                        
                        // Auto-fill coordinates
                        const inputName = inputElement.getAttribute('name') || '';
                        const prefix = inputName.endsWith('location') ? inputName.slice(0, -'location'.length) : '';
                        const latName = prefix + 'latitude';
                        const lngName = prefix + 'longitude';
                        const latField = document.querySelector('[name="' + latName + '"]');
                        const lngField = document.querySelector('[name="' + lngName + '"]');
                        
                        if (latField && lngField && item.latitude && item.longitude) {{
                            const latNum = Number(item.latitude);
                            const lngNum = Number(item.longitude);
                            const latVal = Number.isFinite(latNum) ? latNum.toFixed(6) : item.latitude;
                            const lngVal = Number.isFinite(lngNum) ? lngNum.toFixed(6) : item.longitude;
                            latField.value = latVal;
                            lngField.value = lngVal;
                            showStatus('Coordinates filled: ' + item.latitude + ', ' + item.longitude, 'success');
                            
                            // Trigger change events
                            latField.dispatchEvent(new Event('change', {{ bubbles: true }}));
                            lngField.dispatchEvent(new Event('change', {{ bubbles: true }}));
                            
                            console.log('[Autocomplete] Coordinates auto-filled');
                        }} else {{
                            console.warn('[Autocomplete] Could not fill coordinates. latField: ' + !!latField + ', lngField: ' + !!lngField + ', lat: ' + item.latitude + ', lng: ' + item.longitude);
                        }}
                    }}
                    
                    function fetchSuggestions(query) {{
                        if (query.length < 2) {{
                            hideDropdown();
                            clearStatus();
                            return;
                        }}
                        
                        const inputName = inputElement.getAttribute('name') || '';
                        const prefix = inputName.endsWith('location') ? inputName.slice(0, -'location'.length) : '';
                        const cityName = prefix + cityFieldName;
                        const cityField = document.querySelector('[name="' + cityName + '"]');
                        const city = cityField ? cityField.value.trim() : '';
                        
                        if (!city) {{
                            showStatus('Please select city first', 'warning');
                            hideDropdown();
                            return;
                        }}
                        
                        console.log('[Autocomplete] Fetching: query=' + query + ', city=' + city);
                        
                        const url = '/api/autocomplete-location/?q=' + encodeURIComponent(query) + '&city=' + encodeURIComponent(city);
                        
                        fetch(url)
                            .then(function(response) {{
                                console.log('[Autocomplete] API Response: ' + response.status);
                                if (response.status === 429) {{
                                    showStatus('Rate limit exceeded. Please try again later.', 'error');
                                    hideDropdown();
                                    return;
                                }}
                                if (response.status >= 500) {{
                                    showStatus('API error. Please enter coordinates manually.', 'error');
                                    hideDropdown();
                                    return;
                                }}
                                return response.json();
                            }})
                            .then(function(data) {{
                                if (!data) return;
                                
                                console.log('[Autocomplete] Data received:', data);
                                
                                if (data.api_status === 'api_down') {{
                                    showStatus('Location service unavailable. Enter manually.', 'error');
                                    hideDropdown();
                                    return;
                                }}
                                
                                results = data.results || [];
                                
                                if (results.length > 0) {{
                                    createDropdown(results);
                                    showStatus('Found ' + results.length + ' result(s)', 'success');
                                }} else {{
                                    hideDropdown();
                                    showStatus('No locations found', 'warning');
                                }}
                            }})
                            .catch(function(error) {{
                                console.error('[Autocomplete] Fetch error:', error);
                                showStatus('Error fetching locations. Please enter manually.', 'error');
                                hideDropdown();
                            }});
                    }}
                    
                    // Event handlers
                    inputElement.addEventListener('input', function(e) {{
                        const query = e.target.value.trim();
                        console.log('[Autocomplete] Input: ' + query);
                        fetchSuggestions(query);
                    }});
                    
                    inputElement.addEventListener('focus', function(e) {{
                        const query = e.target.value.trim();
                        if (query.length >= 2 && results.length > 0) {{
                            createDropdown(results);
                        }}
                    }});
                    
                    document.addEventListener('click', function(e) {{
                        if (e.target !== inputElement && (!dropdown || !dropdown.contains(e.target))) {{
                            hideDropdown();
                        }}
                    }});

                    window.addEventListener('resize', positionDropdown);
                    window.addEventListener('scroll', positionDropdown, true);
                    
                    console.log('[Autocomplete] Initialized successfully');
                    
                }} catch (error) {{
                    console.error('[Autocomplete] Initialization error:', error);
                }}
            }}, 100);
        }})();
        </script>
        """
        
        return js_code
    
    class Media:
        css = {
            'all': ()
        }
        js = ()
