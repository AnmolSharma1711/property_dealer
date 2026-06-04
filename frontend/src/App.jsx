import React, { useState, useEffect } from "react";
import apiClient, { API_BASE_URL } from "./utils/api";
import PropertyCard from "./components/PropertyCard";

export default function App() {
	const [localities, setLocalities] = useState([]);
	const [selectedLocality, setSelectedLocality] = useState(null);
	const [properties, setProperties] = useState([]);

	// Initialize CSRF token on app load
	useEffect(() => {
		// Try to get CSRF token from the backend
		const initializeCSRF = async () => {
			try {
				// Make a GET request to any endpoint to trigger Django to set CSRF cookie
				await apiClient.get("localities/", { timeout: 5000 });
				console.log("✓ CSRF token initialized");
			} catch (err) {
				console.warn("Could not initialize CSRF token:", err.message);
			}
		};

		initializeCSRF();
	}, []);

	useEffect(() => {
		fetchLocalities();
		const interval = setInterval(fetchLocalities, 10000);
		return () => clearInterval(interval);
	}, []);

	// Refresh selected locality every 5 seconds to show AI analysis
	useEffect(() => {
		if (!selectedLocality) return;

		const refreshTimer = setInterval(async () => {
			try {
				const res = await apiClient.get(
					`localities/${selectedLocality.id}/`,
				);
				setSelectedLocality(res.data);
			} catch (err) {
				console.error("Error refreshing locality:", err);
			}
		}, 5000);

		return () => clearInterval(refreshTimer);
	}, [selectedLocality]);

	const fetchLocalities = async () => {
		try {
			const res = await apiClient.get("localities/");
			setLocalities(res.data);
		} catch (err) {
			console.error("Error fetching localities:", err);
		}
	};

	const handleLocalitySelect = async (loc) => {
		setSelectedLocality(loc);

		// Trigger AI enrichment if not already done
		if (!loc.profile) {
			try {
				await apiClient.post(`localities/${loc.id}/enrich/`);
				console.log(`✓ AI analysis queued for ${loc.name}`);
			} catch (err) {
				console.error("Error triggering enrichment:", err);
			}
		}

		try {
			const res = await apiClient.get(`localities/${loc.id}/properties/`);
			setProperties(res.data);
		} catch (err) {
			console.error("Error fetching properties for locality:", err);
		}
	};

	return (
		<div className="min-h-screen bg-gradient-to-br from-krishna-50 via-peacock-50 to-saffron-50 flex flex-col">
			{/* Decorative peacock feathers background */}
			<div className="fixed top-0 left-0 w-full h-full pointer-events-none overflow-hidden">
				<div className="absolute top-10 right-10 w-40 h-40 rounded-full bg-gradient-to-br from-peacock-200 to-peacock-100 opacity-20 blur-3xl"></div>
				<div className="absolute bottom-20 left-10 w-60 h-60 rounded-full bg-gradient-to-tr from-krishna-200 to-krishna-100 opacity-15 blur-3xl"></div>
			</div>

			<header className="relative z-10 bg-gradient-krishna border-b-4 border-saffron-400 px-8 py-6 shadow-lg">
				<div className="max-w-7xl mx-auto">
					<div className="flex items-center gap-3 mb-1">
						<span className="text-3xl">🦚</span>
						<h1 className="text-3xl font-bold tracking-tight text-white">
							Property Broker AI
						</h1>
					</div>
					<p className="text-sm text-krishna-100 mt-1">
						✨ Discover divine properties through divine insights
					</p>
				</div>
			</header>

			<main className="relative z-10 flex-1 p-8 grid grid-cols-1 lg:grid-cols-12 gap-8 max-w-7xl mx-auto w-full">
				<div className="lg:col-span-4 bg-white/80 backdrop-blur p-6 rounded-xl border-2 border-krishna-200 shadow-lg h-fit card-divine">
					<h2 className="text-sm font-bold uppercase tracking-wider text-gradient-divine mb-4">
						🏛️ Analyzed Localities
					</h2>
					{localities.length === 0 ? (
						<p className="text-xs text-krishna-400 italic">
							No locations in database yet. Add via Django Admin.
						</p>
					) : (
						<div className="space-y-2">
							{localities.map((loc) => (
								<div
									key={loc.id}
									onClick={() => handleLocalitySelect(loc)}
									className={`p-3.5 rounded-lg border-2 cursor-pointer transition text-left ${selectedLocality?.id === loc.id ? "border-peacock-400 bg-gradient-to-r from-krishna-50 to-peacock-50 shadow-md" : "border-krishna-100 hover:border-peacock-300"}`}
								>
									<h3 className="font-semibold text-sm text-krishna-900">
										{loc.name}
									</h3>
									<p className="text-xs text-krishna-500">
										{loc.city}
									</p>
									{loc.profile ? (
										<span className="inline-block mt-1.5 bg-peacock-50 text-peacock-700 border-2 border-peacock-200 px-2 py-0.5 text-[10px] font-semibold rounded-full">
											✓ Analyzed
										</span>
									) : (
										<span className="inline-block mt-1.5 bg-saffron-50 text-saffron-700 border-2 border-saffron-200 px-2 py-0.5 text-[10px] font-semibold rounded-full animate-pulse">
											⏳ Processing
										</span>
									)}
								</div>
							))}
						</div>
					)}
				</div>

				<div className="lg:col-span-8 space-y-6">
					{selectedLocality ? (
						<>
							<div className="bg-white/80 backdrop-blur p-6 rounded-xl border-2 border-peacock-200 shadow-lg space-y-5 card-divine">
								<div>
									<span className="bg-gradient-krishna text-white font-semibold text-[10px] tracking-widest uppercase px-3 py-1 rounded-full inline-block">
										🤖 Groq LLM Analysis
									</span>
									<h2 className="text-2xl font-bold text-gradient-divine mt-2">
										{selectedLocality.name} Overview
									</h2>
								</div>

								{selectedLocality.profile ? (
									<>
										<p className="text-sm leading-relaxed text-krishna-700 bg-gradient-to-r from-krishna-50 to-peacock-50 p-4 border-l-4 border-saffron-400 rounded-r-lg">
											{selectedLocality.profile.summary}
										</p>

										<div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-2">
											<div className="bg-gradient-to-br from-krishna-50 to-krishna-100 p-3 rounded-lg border-2 border-krishna-200">
												<span className="block text-[10px] uppercase font-bold tracking-wider text-krishna-600">
													👥 Tourism
												</span>
												<span className="text-lg font-bold text-krishna-900">
													{
														selectedLocality.profile
															.tourist_rating
													}
													/5 ★
												</span>
											</div>
											<div className="bg-gradient-to-br from-peacock-50 to-peacock-100 p-3 rounded-lg border-2 border-peacock-200">
												<span className="block text-[10px] uppercase font-bold tracking-wider text-peacock-600">
													🏪 Commerce
												</span>
												<span className="text-lg font-bold text-peacock-900">
													{
														selectedLocality.profile
															.commercial_rating
													}
													/5 ★
												</span>
											</div>
											<div className="bg-gradient-to-br from-saffron-50 to-saffron-100 p-3 rounded-lg border-2 border-saffron-200">
												<span className="block text-[10px] uppercase font-bold tracking-wider text-saffron-600">
													🛍️ Markets
												</span>
												<span className="text-lg font-bold text-saffron-900">
													{
														selectedLocality.profile
															.market_dist_km
													}{" "}
													KM
												</span>
											</div>
											<div className="bg-gradient-to-br from-purple-50 to-purple-100 p-3 rounded-lg border-2 border-purple-200">
												<span className="block text-[10px] uppercase font-bold tracking-wider text-purple-600">
													🚌 Transit
												</span>
												<span className="text-lg font-bold text-purple-900">
													{
														selectedLocality.profile
															.transit_dist_km
													}{" "}
													KM
												</span>
											</div>
										</div>

										<div>
											<h4 className="text-xs font-bold uppercase tracking-wider text-gradient-divine mb-2">
												💎 Recommended Usage
											</h4>
											<div className="flex flex-wrap gap-2">
												{selectedLocality.profile.best_use_suggestions?.map(
													(item, idx) => (
														<span
															key={idx}
															className="bg-peacock-50 text-peacock-700 border-2 border-peacock-200 px-3 py-1 text-xs font-medium rounded-full"
														>
															✓ {item}
														</span>
													),
												)}
											</div>
										</div>

										{/* Infrastructure Analysis - Google-like display */}
										{selectedLocality.profile
											.infrastructure_data &&
											Object.keys(
												selectedLocality.profile
													.infrastructure_data,
											).length > 0 && (
												<div className="bg-gradient-to-br from-krishna-50 to-peacock-50 p-4 rounded-lg border-2 border-krishna-200 space-y-3">
													<h4 className="text-xs font-bold uppercase tracking-wider text-gradient-divine">
														📍 Infrastructure &
														Accessibility
													</h4>
													<div className="grid grid-cols-1 md:grid-cols-2 gap-3">
														{Object.entries(
															selectedLocality
																.profile
																.infrastructure_data,
														).map(
															([key, value]) => (
																<div
																	key={key}
																	className="bg-white/60 p-3 rounded-lg border-2 border-peacock-200"
																>
																	<span className="block text-[10px] font-semibold text-krishna-600 uppercase">
																		{key.replace(
																			/_/g,
																			" ",
																		)}
																	</span>
																	<span className="block text-sm text-krishna-700 mt-1">
																		{value}
																	</span>
																</div>
															),
														)}
													</div>
												</div>
											)}

										{/* Nearby Places - Google Maps style */}
										{selectedLocality.profile
											.nearby_places &&
											Object.keys(
												selectedLocality.profile
													.nearby_places,
											).length > 0 && (
												<div className="space-y-3 border-t-2 border-krishna-200 pt-4">
													<h4 className="text-xs font-bold uppercase tracking-wider text-gradient-divine">
														🏪 Nearby Places (Google
														Maps Data)
													</h4>
													<div className="grid grid-cols-1 md:grid-cols-2 gap-3">
														{Object.entries(
															selectedLocality
																.profile
																.nearby_places,
														).map(
															([
																category,
																data,
															]) => (
																<div
																	key={
																		category
																	}
																	className="bg-gradient-to-br from-peacock-50 to-peacock-100 p-4 rounded-lg border-2 border-peacock-300"
																>
																	<div className="flex items-center justify-between mb-2">
																		<span className="font-bold text-peacock-900 capitalize">
																			{category.replace(
																				/_/g,
																				" ",
																			)}
																		</span>
																		<span className="bg-gradient-peacock text-white text-xs font-bold px-2 py-1 rounded-full">
																			{
																				data.count
																			}
																		</span>
																	</div>
																	<span className="block text-sm text-peacock-700 mb-2">
																		⭐ Avg
																		Rating:{" "}
																		<span className="font-bold">
																			{
																				data.avg_rating
																			}
																			/5
																		</span>
																	</span>
																	{data.places &&
																		data
																			.places
																			.length >
																			0 && (
																			<div className="space-y-1.5 max-h-32 overflow-y-auto">
																				{data.places
																					.slice(
																						0,
																						3,
																					)
																					.map(
																						(
																							place,
																							idx,
																						) => (
																							<div
																								key={
																									idx
																								}
																								className="text-xs bg-white/60 p-2 rounded border-2 border-peacock-200"
																							>
																								<div className="font-semibold text-krishna-800">
																									{
																										place.title
																									}
																								</div>
																								{place.rating && (
																									<div className="text-[10px] text-krishna-600">
																										⭐{" "}
																										{
																											place.rating
																										}
																									</div>
																								)}
																								{place.address && (
																									<div className="text-[10px] text-krishna-500">
																										{place.address.substring(
																											0,
																											50,
																										)}
																										...
																									</div>
																								)}
																							</div>
																						),
																					)}
																				{data
																					.places
																					.length >
																					3 && (
																					<div className="text-xs text-peacock-600 font-semibold pt-1">
																						+
																						{data
																							.places
																							.length -
																							3}{" "}
																						more
																					</div>
																				)}
																			</div>
																		)}
																</div>
															),
														)}
													</div>
												</div>
											)}
									</>
								) : (
									<div className="p-4 bg-gradient-to-r from-saffron-50 to-saffron-100 text-saffron-700 border-2 border-saffron-300 rounded-lg text-xs font-medium animate-pulse">
										⏳ Analysis is being generated by the
										backend. Refresh in a few seconds.
									</div>
								)}
							</div>

							<div className="space-y-3">
								<h3 className="text-sm font-bold uppercase tracking-wider text-gradient-divine">
									🏠 Listings in Area
								</h3>
								{properties.length === 0 ? (
									<div className="bg-white/80 backdrop-blur border-2 border-krishna-200 rounded-xl p-8 text-center text-krishna-400 text-sm">
										No properties listed in this location
										yet.
									</div>
								) : (
									<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
										{properties.map((p) => (
											<PropertyCard
												key={p.id}
												property={p}
												locality={selectedLocality}
											/>
										))}
									</div>
								)}
							</div>
						</>
					) : (
						<div className="bg-white border-2 border-dashed border-slate-200 rounded-xl p-12 text-center text-slate-400 text-sm">
							Select a location to view AI analytics.
						</div>
					)}
				</div>
			</main>

			<footer className="bg-white border-t border-slate-200 px-8 py-4 text-xs text-slate-500 text-center">
				<p>
					Manage properties and localities via{" "}
					<a
						href={`${API_BASE_URL.replace("/api", "")}/admin/`}
						target="_blank"
						rel="noopener noreferrer"
						className="font-semibold text-slate-700 hover:text-slate-900"
					>
						Django Admin Portal
					</a>
				</p>
			</footer>
		</div>
	);
}
