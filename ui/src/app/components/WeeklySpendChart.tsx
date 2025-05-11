import { LineChart } from "@mui/x-charts/LineChart";
import { useEffect, useState } from "react";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
import Skeleton from "@mui/material/Skeleton";

export function DailySpendChart() {
  const [year, setYear] = useState<number>(new Date().getFullYear());
  const [month, setMonth] = useState<number>(new Date().getMonth() + 1);
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    fetch(`/api/analytics/daily_spend?year=${year}&month=${month}`)
      .then((res) => res.json())
      .then((d) => {
        setData(d.daily_spend);
        setLoading(false);
      })
      .catch(() => {
        setError("Failed to load daily spend data");
        setLoading(false);
      });
  }, [year, month]);

  // Only use the overall attribute for the chart
  let rows: any[] = [];
  if (data && Array.isArray(data.overall)) {
    rows = data.overall;
  }

  const noData = !rows.length;

  // Prepare data for the line chart
  const dateLabels = rows.map((row) => {
    const y = row._id?.year;
    const m = row._id?.month;
    const d = row._id?.day;
    return y && m && d
      ? `${y}-${String(m).padStart(2, "0")}-${String(d).padStart(2, "0")}`
      : "";
  });
  const spendData = rows.map((row) => row.total_spend);

  let total = 0;
  if (spendData.length > 0) {
    total = spendData.reduce((a, b) => a + b, 0);
  }

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
          Daily Spend (Current Year)
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
          <LineChart
            xAxis={[
              {
                scaleType: "point",
                data: dateLabels,
                label: "Date",
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
        {!loading && noData && (
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
