import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import App from './App.tsx';
import HomePage from './pages/Home.tsx';
import ScanDashboard from './pages/ScanDashboard.tsx';
import './index.css';

const router = createBrowserRouter([
    {
        path: '/',
        element: <App />,
        children: [
            {
                index: true,
                element: <HomePage />,
            },
            {
                path: 'scan/:scanId',
                element: <ScanDashboard />,
            },
        ],
    },
]);

const Router: React.FC = () => {
    return <RouterProvider router={router} />;
};

export default Router;