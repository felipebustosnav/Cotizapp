import React from 'react';
import { FiBell, FiSearch, FiLogOut } from 'react-icons/fi';
import { useAuth } from '../../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import './Header.css';

import quotationsService from '../../services/quotations.service';

import { useNotifications } from '../../context/NotificationContext';

const Header = () => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const { refreshTrigger } = useNotifications();
    const [pendingCount, setPendingCount] = React.useState(0);

    React.useEffect(() => {
        loadStats();
        // Polling cada 30s
        const interval = setInterval(loadStats, 30000);
        return () => clearInterval(interval);
    }, [refreshTrigger]);

    const loadStats = async () => {
        try {
            const data = await quotationsService.getPendingStats();
            // Backend returns { count: N }
            setPendingCount(data.count !== undefined ? data.count : (data.pendientes || 0));
        } catch (err) {
            console.error('Error loading stats:', err);
        }
    };

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <header className="header">
            <div className="header-search">
                <FiSearch size={20} />
                <input
                    type="text"
                    placeholder="Buscar..."
                    className="header-search-input"
                />
            </div>

            <div className="header-actions">
                <button className="header-notification" onClick={() => navigate('/cotizaciones?pending=true')}>
                    <FiBell size={20} />
                    {pendingCount > 0 && <span className="notification-badge">{pendingCount}</span>}
                </button>

                <div className="header-user">
                    <div className="header-user-info">
                        <p className="header-user-name">{user?.first_name} {user?.last_name}</p>
                        <p className="header-user-email">{user?.email}</p>
                    </div>
                    <button className="header-logout" onClick={handleLogout} title="Cerrar sesión">
                        <FiLogOut size={18} />
                    </button>
                </div>
            </div>
        </header>
    );
};

export default Header;
