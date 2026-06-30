import { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

// Fix for Vite marker icons missing in production
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconUrl: markerIcon,
  iconRetinaUrl: markerIcon2x,
  shadowUrl: markerShadow,
});

export default function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [aiResult, setAiResult] = useState(null);
  
  const [markerPosition, setMarkerPosition] = useState([18.5204, 73.8567]); 
  const [currentCity, setCurrentCity] = useState("Pune");
  const [savedIssues, setSavedIssues] = useState([]);

  // Fetch all issues from the database
  const fetchIssues = async () => {
    try {
      const res = await fetch("/api/issues", {
        headers: {
          "Bypass-Tunnel-Reminder": "true" // 👈 Localtunnel bypass for GET request
        }
      });
      const data = await res.json();
      setSavedIssues(data);
    } catch (err) {
      console.error("Failed to fetch database issues", err);
    }
  };

  useEffect(() => {
    fetchIssues();
  }, []);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return alert("Please select an image first!");

    setLoading(true);
    const formData = new FormData();
    formData.append("file", file);
    formData.append("lat", markerPosition[0]);
    formData.append("lng", markerPosition[1]);
    formData.append("city", currentCity);

    try {
      const response = await fetch("/api/issues/report", {
        method: "POST",
        body: formData,
        headers: {
          "Bypass-Tunnel-Reminder": "true" // 👈 Localtunnel bypass for POST request
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setAiResult(data.ai_analysis);
      fetchIssues(); // Refresh map with new issue
    } catch (error) {
      console.error("Upload failed:", error);
      alert("Failed to connect to the AI API. Check terminal logs or try a smaller image size.");
    } finally {
      setLoading(false);
    }
  };

  // Handle map clicks & automatic City detection via reverse geocoding
  function LocationSelector() {
    useMapEvents({
      async click(e) {
        const lat = e.latlng.lat;
        const lng = e.latlng.lng;
        setMarkerPosition([lat, lng]);
        setAiResult(null); 
        
        try {
          const res = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`);
          const data = await res.json();
          const detectedCity = data.address.city || data.address.town || data.address.state_district || "Unknown Location";
          setCurrentCity(detectedCity);
        } catch (err) {
          setCurrentCity("Unknown Location");
        }
      },
    });

    return (
      <Marker position={markerPosition} opacity={0.5}>
        <Popup>Target: {currentCity}</Popup>
      </Marker>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 p-8 font-sans">
      <header className="mb-8 text-center">
        <h1 className="text-4xl font-bold text-blue-600">Community Hero</h1>
        <p className="text-gray-600 mt-2">Hyperlocal AI Problem Solver</p>
      </header>

      <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-8">
        
        {/* Left Side: The Map */}
        <div className="bg-white p-4 rounded-xl shadow-lg h-[500px]">
          <h2 className="text-xl font-semibold mb-1 text-gray-800">Live Issue Map</h2>
          <p className="text-sm text-gray-500 mb-3 font-medium">👉 Click map to drop target pin, then upload image.</p>
          <MapContainer center={[18.5204, 73.8567]} zoom={13} className="h-[380px] w-full rounded-lg z-0">
            <TileLayer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution='&copy; OpenStreetMap contributors'
            />
            
            <LocationSelector />

            {/* Render all saved issues */}
            {savedIssues.map((issue) => (
              <Marker key={issue.id} position={[issue.lat, issue.lng]}>
                <Popup>
                  <div className="text-sm text-gray-800">
                    <strong className="text-blue-600 border-b block pb-1 mb-1">{issue.category}</strong>
                    <p className="text-xs text-gray-500 mb-1">📍 {issue.city}</p>
                    <p className={`mb-1 font-semibold ${issue.severity === 'High' ? 'text-red-600' : 'text-orange-500'}`}>
                      Severity: {issue.severity}
                    </p>
                    <p className="text-gray-600">{issue.description}</p>
                  </div>
                </Popup>
              </Marker>
            ))}
          </MapContainer>
        </div>

        {/* Right Side: Upload Form */}
        <div className="bg-white p-6 rounded-xl shadow-lg flex flex-col justify-center">
          <h2 className="text-2xl font-semibold mb-6 text-gray-800">Report an Issue</h2>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:bg-gray-50 transition cursor-pointer">
              <input 
                type="file" 
                accept="image/*" 
                onChange={handleFileChange}
                className="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
              />
            </div>
            
            <button 
              type="submit" 
              disabled={loading}
              className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition disabled:bg-blue-300"
            >
              {loading ? "AI is analyzing & saving to DB..." : "Analyze with Gemini"}
            </button>
          </form>

          {aiResult && (
            <div className="mt-8 p-4 bg-green-50 border border-green-200 rounded-lg text-gray-800">
              <h3 className="text-lg font-bold text-green-800 mb-2">Issue Logged to Database!</h3>
              <p><strong>Category:</strong> {aiResult.category}</p>
              <p><strong>Severity:</strong> {aiResult.severity}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
