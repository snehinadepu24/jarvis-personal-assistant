import React from 'react';
import { OrbWindow } from './windows/OrbWindow';
import { DashboardWindow } from './windows/DashboardWindow';

export const App: React.FC = () => {
  const params = new URLSearchParams(window.location.search);
  const windowType = params.get('window') || 'dashboard';

  if (windowType === 'orb') {
    return <OrbWindow />;
  }

  return <DashboardWindow />;
};

export default App;

