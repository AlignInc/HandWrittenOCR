import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import UploadZone from './components/UploadZone';
import ResultsView from './components/ResultsView';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<UploadZone />} />
        <Route path="/results/:batchId" element={<ResultsView />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
