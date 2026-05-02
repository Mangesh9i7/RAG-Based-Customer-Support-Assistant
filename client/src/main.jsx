import { createRoot } from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import "./index.css";
// import Navebar from "./langingPage/Navbar";
import HomePage from "./components/home/HomePage";
import ChatPage from "./components/chat/ChatPage";

createRoot(document.getElementById("root")).render(
  <BrowserRouter>
    {/* <Navebar /> */}
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/chat" element={<ChatPage />} />
    </Routes>
  </BrowserRouter>,
);
