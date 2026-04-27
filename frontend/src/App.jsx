import { Navigate, Route, Routes } from "react-router-dom";

import { CheckoutPage } from "./pages/CheckoutPage";
import { HistoryPage } from "./pages/HistoryPage";

export default function App() {
  return (
    <div className="page-shell">
      <Routes>
        <Route path="/" element={<Navigate to="/checkout" replace />} />
        <Route path="/checkout" element={<CheckoutPage />} />
        <Route path="/history" element={<HistoryPage />} />
      </Routes>
    </div>
  );
}
