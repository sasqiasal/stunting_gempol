/**
 * Map Component with Leaflet
 * Menampilkan peta dengan marker posyandu dan polygon dari GeoJSON
 */

import React, { useEffect, useRef, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup, Polygon, useMap, GeoJSON } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { posyanduService } from "../services/posyanduService";
import toast from "react-hot-toast";

// Fix Leaflet default marker icon
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png",
  iconUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png",
  shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
});

// Custom marker icons based on stunting level
const getMarkerIcon = (stuntingCount) => {
  let color = "#22c55e"; // green (normal)

  if (stuntingCount >= 2) {
    color = "#dc2626"; // red (high)
  } else if (stuntingCount === 1) {
    color = "#f59e0b"; // yellow (medium)
  }

  return L.divIcon({
    className: "custom-marker",
    html: `
      <div style="
        background-color: ${color};
        width: 32px;
        height: 32px;
        border-radius: 50%;
        border: 3px solid white;
        box-shadow: 0 2px 6px rgba(0,0,0,0.4);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 13px;
      ">
        ${stuntingCount}
      </div>
    `,
    iconSize: [32, 32],
    iconAnchor: [16, 16],
  });
};

// Get polygon style - always use default color from GeoJSON
const getPolygonStyle = (properties) => {
  const defaultFillColor = properties?.fill || "#3b82f6";
  const defaultFillOpacity = properties?.["fill-opacity"] || 0.5;

  return {
    fillColor: defaultFillColor,
    weight: 2,
    opacity: 1,
    color: "white",
    fillOpacity: defaultFillOpacity,
  };
};

/**
 * Component to handle map events
 */
const MapEvents = ({ onPosyanduClick }) => {
  const map = useMap();

  useEffect(() => {
    // Add any map event handlers here if needed
  }, [map]);

  return null;
};

/**
 * Main Map Component
 */
export const StuntingMap = ({ onPosyanduSelect }) => {
  const [posyanduData, setPosyanduData] = useState(null);
  const [posyanduList, setPosyanduList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedPosyandu, setSelectedPosyandu] = useState(null);

  // Default center (Gempol - center dari GeoJSON Anda)
  const defaultCenter = [-7.551, 112.7];
  const defaultZoom = 100;

  // Load GeoJSON file dan data posyandu dari API
  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);

      // Load GeoJSON polygon untuk wilayah boundaries
      const geoResponse = await fetch(`/map.geojson?v=${Date.now()}`);
      const polygonData = await geoResponse.json();

      // Load data posyandu dari API database (nama terbaru + statistik)
      const posyanduData = await posyanduService.getAll();

      console.log("📍 Data Posyandu dari Database:", posyanduData);

      // Merge: gunakan NAMA dari DATABASE (bukan dari geojson static)
      const mergedFeatures = polygonData.features.map((feature, index) => {
        const geojsonName = feature.properties?.nama_posyandu || feature.properties?.nama;

        if (!geojsonName) {
          console.warn(`⚠️ Feature ${index}: No name found`);
          return feature;
        }

        // Exact match - nama di geojson dan database sekarang sudah sama persis
        const matchedPosyandu = posyanduData.find((p) => {
          if (!p.nama) return false;
          
          // Case-insensitive exact match (hapus spasi ekstra saja)
          const dbName = p.nama.toLowerCase().trim();
          const geoName = geojsonName.toLowerCase().trim();
          
          return dbName === geoName;
        });

        if (matchedPosyandu) {
          console.log(`✅ Feature ${index}: "${geojsonName}" → Matched DB ID ${matchedPosyandu.id} (${matchedPosyandu.jumlah_stunting} stunting, ${matchedPosyandu.jumlah_balita} balita)`);
        } else {
          console.error(`❌ Feature ${index}: "${geojsonName}" → NO MATCH in database!`);
        }

        return {
          ...feature,
          properties: {
            ...feature.properties,
            // GUNAKAN NAMA DARI DATABASE (bukan dari geojson static)
            nama: matchedPosyandu?.nama || geojsonName,
            nama_posyandu: matchedPosyandu?.nama || geojsonName,
            stunting: matchedPosyandu?.jumlah_stunting || 0,
            jumlah_stunting: matchedPosyandu?.jumlah_stunting || 0,
            jumlah_balita: matchedPosyandu?.jumlah_balita || 0,
            posyandu_id: matchedPosyandu?.id,
            kader_penanggungjawab: matchedPosyandu?.kader_penanggungjawab,
          },
        };
      });

      setPosyanduData({ ...polygonData, features: mergedFeatures });
      setPosyanduList(posyanduData);
    } catch (error) {
      console.error("Error loading data:", error);
      toast.error("Gagal memuat data peta");
    } finally {
      setLoading(false);
    }
  };

  const handleMarkerClick = (posyandu) => {
    setSelectedPosyandu(posyandu);
    if (onPosyanduSelect) {
      onPosyanduSelect(posyandu.properties);
    }
  };

  if (loading) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-gray-100">
        <div className="text-center">
          <div className="spinner mx-auto"></div>
          <p className="mt-2 text-gray-600">Memuat peta...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full w-full relative">
      <MapContainer center={[-7.55, 112.7]} zoom={15} minZoom={15} maxZoom={16} className="h-full w-full z-0" scrollWheelZoom={false}>
        <TileLayer attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />

        {/* Render GeoJSON Features */}
        {posyanduData?.features?.map((feature, index) => {
          const { geometry, properties } = feature;
          const nama_posyandu = properties?.nama || properties?.nama_posyandu || "Posyandu";
          const stuntingCount = properties?.jumlah_stunting || properties?.stunting || 0;

          // Hitung centroid untuk marker
          let center = [0, 0];
          if (geometry.type === "Polygon") {
            const coords = geometry.coordinates[0];
            const lats = coords.map((c) => c[1]);
            const lngs = coords.map((c) => c[0]);
            center = [lats.reduce((a, b) => a + b, 0) / lats.length, lngs.reduce((a, b) => a + b, 0) / lngs.length];
          } else if (geometry.type === "Point") {
            center = [geometry.coordinates[1], geometry.coordinates[0]];
          }

          return (
            <React.Fragment key={index}>
              {/* Polygon */}
              {geometry.type === "Polygon" && (
                <Polygon
                  positions={geometry.coordinates[0].map((coord) => [coord[1], coord[0]])}
                  pathOptions={getPolygonStyle(properties)}
                  eventHandlers={{
                    click: () => handleMarkerClick(feature),
                  }}
                >
                  <Popup>
                    <div className="p-3 min-w-[220px]">
                      <h3 className="font-bold text-lg mb-3 text-gray-900 border-b pb-2">{nama_posyandu}</h3>

                      {/* Jumlah Anak Stunting */}
                      <div className="bg-gray-50 rounded-lg p-3 mb-2">
                        <div className="text-center">
                          <div className={`text-3xl font-bold mb-1 ${stuntingCount >= 2 ? "text-red-600" : stuntingCount === 1 ? "text-orange-600" : "text-green-600"}`}>{stuntingCount}</div>
                          <div className="text-xs text-gray-600 uppercase tracking-wide">Anak Terindikasi Stunting</div>
                        </div>
                      </div>

                      {/* Status */}
                      <div className="flex items-center justify-center gap-2 mt-2">
                        <span
                          className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${
                            stuntingCount >= 2 ? "bg-red-100 text-red-700" : stuntingCount === 1 ? "bg-orange-100 text-orange-700" : "bg-green-100 text-green-700"
                          }`}
                        >
                          {stuntingCount >= 2 ? "TINGGI" : stuntingCount === 1 ? "SEDANG" : "AMAN"}
                        </span>
                      </div>

                      {stuntingCount > 0 && <div className="mt-3 pt-2 border-t text-xs text-gray-500 text-center">Perlu perhatian khusus</div>}
                    </div>
                  </Popup>
                </Polygon>
              )}

              {/* Marker di center polygon - hanya tampil jika ada stunting */}
              {stuntingCount > 0 && (
                <Marker
                  position={center}
                  icon={getMarkerIcon(stuntingCount)}
                  eventHandlers={{
                    click: () => handleMarkerClick(feature),
                  }}
                >
                  <Popup>
                    <div className="p-3 min-w-[220px]">
                      <h3 className="font-bold text-lg mb-3 text-gray-900 border-b pb-2">{nama_posyandu}</h3>

                      {/* Jumlah Anak Stunting */}
                      <div className="bg-gray-50 rounded-lg p-3 mb-2">
                        <div className="text-center">
                          <div className={`text-3xl font-bold mb-1 ${stuntingCount >= 2 ? "text-red-600" : stuntingCount === 1 ? "text-orange-600" : "text-green-600"}`}>{stuntingCount}</div>
                          <div className="text-xs text-gray-600 uppercase tracking-wide">Anak Terindikasi Stunting</div>
                        </div>
                      </div>

                      {/* Status */}
                      <div className="flex items-center justify-center gap-2 mt-2">
                        <span
                          className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${
                            stuntingCount >= 2 ? "bg-red-100 text-red-700" : stuntingCount === 1 ? "bg-orange-100 text-orange-700" : "bg-green-100 text-green-700"
                          }`}
                        >
                          {stuntingCount >= 2 ? "TINGGI" : stuntingCount === 1 ? "SEDANG" : "AMAN"}
                        </span>
                      </div>

                      {stuntingCount > 0 && <div className="mt-3 pt-2 border-t text-xs text-gray-500 text-center">Perlu perhatian khusus</div>}
                    </div>
                  </Popup>
                </Marker>
              )}
            </React.Fragment>
          );
        })}
      </MapContainer>

      {/* Legend - Updated */}
      <div className="absolute bottom-4 right-4 bg-white p-3 sm:p-4 rounded-lg shadow-lg z-[1000] text-xs sm:text-sm">
        <h4 className="font-bold mb-2">Legenda Peta</h4>
        <div className="space-y-2">
          <div className="text-xs font-semibold text-gray-700 mb-1">Indikator Stunting:</div>
          <div className="space-y-1.5">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded-full bg-orange-500 border-2 border-white shadow"></div>
              <span className="text-xs">1 anak stunting</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded-full bg-red-600 border-2 border-white shadow"></div>
              <span className="text-xs">≥2 anak stunting</span>
            </div>
          </div>
        </div>
        <div className="mt-2 pt-2 border-t text-xs text-gray-500">{posyanduData?.features?.length || 0} Posyandu</div>
      </div>
    </div>
  );
};

export default StuntingMap;
