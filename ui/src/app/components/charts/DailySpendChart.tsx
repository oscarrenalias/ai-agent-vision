import { BarChart } from "@mui/x-charts/BarChart";
import { useEffect, useState } from "react";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
import Skeleton from "@mui/material/Skeleton";

export function DailySpendChart({
  year,
  month,
}: {
  year: number;
  month: number;
}) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    fetch(`/api/analytics/daily_spend?year=${year}&month=${month}`)
      .then((res) => res.json())
      .then((d) => {
        setData(d.daily_spend?.overall || []);
        setLoading(false);
      })
      .catch(() => {
        setError("Failed to load daily spend data");
        setLoading(false);
      });
  }, [year, month]);

  let rows: any[] = [];
  if (data && Array.isArray(data)) {
    rows = data;
  }

  const daysInMonth = new Date(year, month, 0).getDate();
  const allDays: string[] = [];
  for (let d = 1; d <= daysInMonth; d++) {
    allDays.push(String(d).padStart(2, "0"));
  }

  // Map spend data to all days in the month, filling missing days with 0
  const spendMap = new Map<string, number>();
  rows.forEach((row) => {
    const d = row._id?.day;
    if (d) {
      const key = String(d).padStart(2, "0");
      spendMap.set(key, row.total_spend);
    }
  });
  const spendData = allDays.map((day) => spendMap.get(day) || 0);

  let total = 0;
  if (spendData.length > 0) {
    total = spendData.reduce((a, b) => a + b, 0);
  }

  // Get month name for title
  const monthName = new Date(year, month - 1).toLocaleString("default", {
    month: "long",
  });

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
          {monthName} {year} Daily Spend
        </Typography>
        <Typography variant="subtitle1" align="center" sx={{ mb: 1 }}>
          Month-to-date Total: {total.toFixed(2)} €
        </Typography>
        {loading ? (
          <Skeleton
            variant="rectangular"
            height={260}
            sx={{ borderRadius: 2, mb: 2 }}
          />
        ) : (
          <BarChart
            xAxis={[
              {
                scaleType: "band",
                data: allDays,
                label: "Day",
              },
            ]}
            series={[
              {
                data: spendData,
                label: "Daily Spend (€)",
              },
            ]}
            height={260}
          />
        )}
        {!loading && spendData.every((v) => v === 0) && (
          <Typography
            variant="body2"
            color="text.secondary"
            align="center"
            sx={{ mt: 2 }}
          >
            No data available for this month
          </Typography>
        )}
      </CardContent>
    </Card>
  );
}
