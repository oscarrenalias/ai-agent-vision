import React from "react";
import { YearlySpendChart } from "./components/charts/YearlySpendChart";
import { YearlyMonthlySpendChart } from "./components/charts/YearlyMonthlySpendChart";
import { MonthlySpendChart } from "./components/charts/MonthlySpendChart";
import { DailySpendChart } from "./components/charts/DailySpendChart";
import { MealPlanCard } from "./components/MealPlanCard";
import { ShoppingListCard } from "./components/ShoppingListCard";

interface AnalyticsSectionProps {
  year: number;
  month: number;
  setYear: (y: number) => void;
  setMonth: (m: number) => void;
}

export default function AnalyticsSection({
  year,
  month,
  setYear,
  setMonth,
}: AnalyticsSectionProps) {
  // Handler to sync year/month changes from any chart
  const handleYearChange = (newYear: number) => {
    setYear(newYear);
  };
  const handleMonthChange = (newMonth: number) => {
    setMonth(newMonth);
  };

  return (
    <div>
      <div style={{ display: "flex", gap: 24, marginBottom: 24 }}>
        <div style={{ flex: 1 }}>
          {/* YearlyMonthlySpendChart does not accept setYear, so just pass year */}
          <YearlyMonthlySpendChart year={year} />
        </div>
        <div style={{ flex: 1 }}>
          <MonthlySpendChart
            year={year}
            month={month}
            setYear={handleYearChange}
            setMonth={handleMonthChange}
          />
        </div>
      </div>
      <DailySpendChart year={year} month={month} />
    </div>
  );
}
