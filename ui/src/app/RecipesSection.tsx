import React, { useEffect } from "react";

export default function RecipesSection() {
  useEffect(() => {
    // Fetch all recipes on mount
    fetch("/api/recipes")
      .then((res) => res.json())
      .then((data) => {
        // For now, do nothing with the data
        // You can add state and display logic later
      })
      .catch((err) => {
        // Handle error (optional for now)
      });
  }, []);

  return (
    <div>
      {/* RecipesSection: Will display recipes here in the future */}
    </div>
  );
}
