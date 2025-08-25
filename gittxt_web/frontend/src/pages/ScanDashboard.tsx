import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { getScanSummary, downloadArtifact, ScanResponse, SummaryData } from '../api';
import './ScanDashboard.css';
import InspectDialog from '../components/InspectDialog';

const ScanDashboard: React.FC = () => {
    const { scanId } = useParams<{ scanId: string }>();
    const [scanData, setScanData] = useState<ScanResponse | null>(null);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const [showInspect, setShowInspect] = useState<boolean>(false);
    const [selectedFile, setSelectedFile] = useState<string | null>(null);

    useEffect(() => {
        const fetchSummary = async () => {
            if (!scanId) {
                setError("No scan ID provided.");
                setLoading(false);
                return;
            }

            try {
                setLoading(true);
                const data = await getScanSummary(scanId);
                setScanData(data);
                setError(null);
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to fetch scan summary.');
                console.error('Failed to fetch scan summary:', err);
            } finally {
                setLoading(false);
            }
        };
        fetchSummary();
    }, [scanId]);

    const handleDownload = async () => {
        if (!scanId) {
            setError("No scan ID to download.");
            return;
        }
        try {
            await downloadArtifact(scanId);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to download artifact.');
            console.error('Failed to download artifact:', err);
        }
    };
    
    const handleInspectClick = (filePath: string) => {
        setSelectedFile(filePath);
        setShowInspect(true);
    };

    if (loading) {
        return <div className="loading-container">Loading scan summary...</div>;
    }

    if (error) {
        return <div className="error-container">Error: {error}</div>;
    }

    if (!scanData) {
        return <div className="info-container">No scan data found for this ID.</div>;
    }

    const { repo_name, num_textual_files, summary } = scanData;
    const formattedSummary: SummaryData = summary;
    
    return (
        <div className="dashboard-container">
            <h1 className="dashboard-title">Scan Results for {repo_name}</h1>
            <p className="scan-message">{scanData.message}</p>
            
            <div className="summary-cards">
                <div className="card">
                    <h3>Total Files</h3>
                    <p>{num_textual_files}</p>
                </div>
                <div className="card">
                    <h3>Total Size</h3>
                    <p>{formattedSummary?.formatted.total_size}</p>
                </div>
                <div className="card">
                    <h3>Estimated Tokens</h3>
                    <p>{formattedSummary?.formatted.estimated_tokens}</p>
                </div>
            </div>

            <div className="summary-section">
                <h2>File Type Breakdown</h2>
                <ul className="breakdown-list">
                    {Object.entries(formattedSummary?.file_type_breakdown || {}).map(([type, count]) => (
                        <li key={type}>
                            <strong>{type}:</strong> {count} files
                        </li>
                    ))}
                </ul>
            </div>

            <button onClick={handleDownload} className="download-button">
                Download All Outputs (ZIP)
            </button>
            
            {showInspect && selectedFile && (
                <InspectDialog
                    filePath={selectedFile}
                    scanId={scanId}
                    onClose={() => setShowInspect(false)}
                />
            )}
        </div>
    );
};

export default ScanDashboard;