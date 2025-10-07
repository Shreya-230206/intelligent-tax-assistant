import React, { useState } from "react";
import { motion } from "framer-motion";

// Components
import ProfileTab from "./components/ProfileTab";
import IncomeTab from "./components/IncomeTab";
import TaxationTab from "./components/TaxationTab";
import ReportsTab from "./components/ReportsTab";
import GuidanceTab from "./components/GuidanceTab";

function App() {
  const [formSubmitted, setFormSubmitted] = useState(false);
  const [formData, setFormData] = useState({});
  const [activeTab, setActiveTab] = useState("Profile");

  const handleSubmit = (e) => {
    e.preventDefault();
    setFormSubmitted(true);
  };

  return (
    <div className="min-h-screen bg-[#BAE2BE] text-gray-800">
      {/* Animated Header */}
      <div className="overflow-hidden whitespace-nowrap text-center py-5">
        <motion.h1
          className="text-3xl font-bold text-[#090D42] inline-block"
          animate={{ x: ["-100%", "100%"] }}
          transition={{ repeat: Infinity, duration: 10, ease: "linear" }}
        >
           Tax Assistant – The Future of Tax Planning!
        </motion.h1>
      </div>

      {/* Form Section */}
      {!formSubmitted ? (
        <div className="flex flex-col items-center p-6">
          <form
            onSubmit={handleSubmit}
            className="bg-white rounded-2xl shadow-lg p-8 w-full max-w-xl space-y-4"
          >
            <h2 className="text-2xl font-semibold mb-4">
              1️⃣ Personal Information
            </h2>

            <label className="block font-medium">Select Age Group</label>
            <select
              className="w-full border p-2 rounded-lg"
              onChange={(e) =>
                setFormData({ ...formData, ageGroup: e.target.value })
              }
            >
              <option>Below 60</option>
              <option>60 and above</option>
              <option>80 and above</option>
            </select>

            <label className="block font-medium">Residential Status</label>
            <div className="flex space-x-4">
              <label>
                <input
                  type="radio"
                  name="residential_status"
                  value="Resident"
                  onChange={(e) =>
                    setFormData({ ...formData, residentialStatus: e.target.value })
                  }
                />{" "}
                Resident
              </label>
              <label>
                <input
                  type="radio"
                  name="residential_status"
                  value="Non-Resident"
                  onChange={(e) =>
                    setFormData({ ...formData, residentialStatus: e.target.value })
                  }
                />{" "}
                Non-Resident
              </label>
            </div>

            <label className="block font-medium">
              Financial Year / Assessment Year
            </label>
            <select
              className="w-full border p-2 rounded-lg"
              onChange={(e) =>
                setFormData({ ...formData, fyAy: e.target.value })
              }
            >
              <option>FY 2025-26 / AY 2026-27</option>
            </select>

            <label className="block font-medium">Employment Type</label>
            <select
              className="w-full border p-2 rounded-lg"
              onChange={(e) =>
                setFormData({ ...formData, employmentType: e.target.value })
              }
            >
              <option>Salaried</option>
              <option>Freelancer</option>
              <option>Business</option>
              <option>Rental</option>
              <option>Investor</option>
              <option>Mixed</option>
            </select>

            <button
              type="submit"
              className="w-full bg-[#090D42] text-white py-2 rounded-lg hover:bg-[#141b7a] transition"
            >
              Submit Profile
            </button>
          </form>
        </div>
      ) : (
        <div className="max-w-6xl mx-auto px-6">
          {/* Navigation Tabs */}
          <div className="flex justify-center space-x-6 border-b mb-6">
            {["Profile", "Income Details", "Tax Calculation", "Reports", "Guidance"].map(
              (tab) => (
                <button
                  key={tab}
                  className={`py-2 px-4 font-medium ${
                    activeTab === tab
                      ? "border-b-4 border-[#090D42] text-[#090D42]"
                      : "text-gray-500 hover:text-gray-800"
                  }`}
                  onClick={() => setActiveTab(tab)}
                >
                  {tab}
                </button>
              )
            )}
          </div>

          {/* Conditional Rendering of Tabs */}
          {activeTab === "Profile" && <ProfileTab formData={formData} />}
          {activeTab === "Income Details" && <IncomeTab />}
          {activeTab === "Tax Calculation" && <TaxationTab formData={formData} />}
          {activeTab === "Reports" && <ReportsTab />}
          {activeTab === "Guidance" && <GuidanceTab formData={formData} />}
        </div>
      )}
    </div>
  );
}

export default App;
