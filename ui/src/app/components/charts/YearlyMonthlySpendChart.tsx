import React, { useEffect, useState } from "react";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
import Skeleton from "@mui/material/Skeleton";
import { BarChart } from "@mui/x-charts/BarChart";
import IconButton from "@mui/material/IconButton";
import ArrowBackIosNewIcon from "@mui/icons-material/ArrowBackIosNew";
import ArrowForwardIosIcon from "@mui/icons-material/ArrowForwardIos";

interface BarData {
  month: number;
  [key: string]: number | string;
}

const MONTH_LABELS = [
  "Jan",
  "Feb",
  "Mar",
  "Apr",
  "May",
  "Jun",
  "Jul",
  "Aug",
  "Sep",
  "Oct",
  "Nov",
  "Dec",
];

export function YearlyMonthlySpendChart({
  year: initialYear,
}: {
  year: number;
}) {
  const now = new Date();
  const currentYear = now.getFullYear();
  const [year, setYear] = useState(initialYear || currentYear);
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    fetch(`/api/analytics/yearly_monthly_spend?year=${year}`)
      .then(async (res) => {
        if (!res.ok) throw new Error("Network response was not ok");
        const text = await res.text();
        if (!text) return [];
        try {
          const d = JSON.parse(text);
          return d.yearly_monthly_spend || [];
        } catch {
          return [];
        }
      })
      .then((d) => {
        setData(d);
        setLoading(false);
      })
      .catch(() => {
        setError("Failed to load yearly monthly spend data");
        setLoading(false);
      });
  }, [year]);

  if (error && !data) return <div>{error}</div>;

  // Prepare bar chart data for new structure
  let bars: BarData[] = Array.from({ length: 12 }, (_, i) => ({
    month: i + 1,
  }));
  let level1Keys: string[] = [];

  if (Array.isArray(data)) {
    data.forEach((entry: any) => {
      const m = entry.month;
      if (m) {
        bars[m - 1]["total"] = entry.overall_spend;
        if (Array.isArray(entry.level_1)) {
          entry.level_1.forEach((l1: any) => {
            const key = l1.level_1;
            bars[m - 1][key] = l1.total_spend;
            if (key && !level1Keys.includes(key)) level1Keys.push(key);
          });
        }
      }
    });
  }

  // Only level_1 breakdown or total is available in this structure
  let seriesKeys: string[] = level1Keys.length > 0 ? level1Keys : ["total"];

  const series = seriesKeys.map((key) => ({
    data: bars.map((bar) => (typeof bar[key] === "number" ? bar[key] : 0)),
    label: key,
    stack: "level_1", // Enable stacking for all level_1 keys
  }));

  return (
    <Card sx={{ mb: 3, width: "100%", minWidth: 320, flex: 1 }}>
      <CardContent>
        <Typography
          variant="h6"
          gutterBottom
          sx={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <IconButton
            onClick={() => setYear((y) => Math.max(2000, y - 1))}
            disabled={year <= 2000}
            size="small"
            aria-label="Previous Year"
            sx={{ mr: 1 }}
          >
            <ArrowBackIosNewIcon fontSize="small" />
          </IconButton>
          <span style={{ margin: "0 8px" }}>{year} Monthly Spend</span>
          <IconButton
            onClick={() => setYear((y) => Math.min(currentYear, y + 1))}
            disabled={year >= currentYear}
            size="small"
            aria-label="Next Year"
            sx={{ ml: 1 }}
          >
            <ArrowForwardIosIcon fontSize="small" />
          </IconButton>
        </Typography>
        {loading ? (
          <Skeleton
            variant="rectangular"
            height={320}
            sx={{ borderRadius: 2, mb: 2 }}
          />
        ) : (
          <BarChart
            xAxis={[
              {
                scaleType: "band",
                data: MONTH_LABELS,
                label: "Month",
              },
            ]}
            series={series}
            height={320}
            // Enable stacking
            slotProps={{ legend: { hidden: false } }}
          />
        )}
      </CardContent>
    </Card>
  );
}
