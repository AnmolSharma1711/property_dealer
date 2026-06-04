import axios from "axios";

// Determine API base URL based on environment
const getApiBaseUrl = () => {
	let url;

	// If explicitly set via environment variable (build time)
	if (import.meta.env.VITE_API_URL) {
		url = import.meta.env.VITE_API_URL;
		console.log("Using VITE_API_URL:", url);
	} else if (
		typeof window !== "undefined" &&
		window.location.hostname.includes("onrender.com")
	) {
		// In production on Render static sites
		url = "https://property-dealer-gf4c.onrender.com/api";
		console.log("Detected Render production, using:", url);
	} else {
		// In development, use localhost
		url = "http://localhost:8000/api";
		console.log("Development mode, using:", url);
	}

	// Ensure the URL includes /api path
	if (!url.endsWith("/api") && !url.includes("/api/")) {
		url = url.endsWith("/") ? url + "api" : url + "/api";
		console.log("Appended /api suffix, final URL:", url);
	}

	return url;
};

const API_BASE_URL = getApiBaseUrl();
console.log("API_BASE_URL final value:", API_BASE_URL);

// Create axios instance with default config
const apiClient = axios.create({
	baseURL: API_BASE_URL,
	headers: {
		"Content-Type": "application/json",
	},
});

// Helper to extract CSRF token from cookie
function extractCsrfTokenFromCookie() {
	const cookieName = "csrftoken";
	let tokenValue = null;

	if (document.cookie && document.cookie !== "") {
		const cookieList = document.cookie.split(";");
		for (let i = 0; i < cookieList.length; i++) {
			const cookieItem = cookieList[i].trim();
			if (
				cookieItem.substring(0, cookieName.length + 1) ===
				cookieName + "="
			) {
				tokenValue = decodeURIComponent(
					cookieItem.substring(cookieName.length + 1),
				);
				break;
			}
		}
	}

	return tokenValue;
}

// Add auth token and CSRF token to requests
apiClient.interceptors.request.use((config) => {
	// Add stored auth token if available
	const authToken = localStorage.getItem("authToken");
	if (authToken) {
		config.headers.Authorization = `Bearer ${authToken}`;
	}

	// Add CSRF token for Django protection
	const csrfTokenFromCookie = extractCsrfTokenFromCookie();
	if (csrfTokenFromCookie) {
		config.headers["X-CSRFToken"] = csrfTokenFromCookie;
	}

	return config;
});

// Handle errors
apiClient.interceptors.response.use(
	(response) => response,
	(error) => {
		if (error.response?.status === 401) {
			localStorage.removeItem("authToken");
			window.location.href = "/login";
		}
		return Promise.reject(error);
	},
);

export default apiClient;
export { API_BASE_URL };
