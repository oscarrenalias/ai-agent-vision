import { BarChart } from "@mui/x-charts/BarChart";
import { useEffect, useState } from "react";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";

export function YearlySpendBarChart() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/analytics/yearly_spend")
      .then((res) => res.json())
      .then((d) => {
        setData(d.yearly_spend);
        setLoading(false);
      })
      .catch((e) => {
        setError("Failed to load yearly spend data");
        setLoading(false);
      });
  }, []);

  if (loading) return <div>Loading yearly spend...</div>;
  if (error) return <div>{error}</div>;
  if (!data) return null;

  // Extract the year from the first overall entry, fallback to empty if not found
  const year =
    data.overall && data.overall[0]?._id?.year ? data.overall[0]._id.year : "";

  // Show all level_2 as bars, grouped by level_1
  const rows = data.level_2.map((l2: any) => ({
    level_1: l2.level_1,
    level_2: l2.level_2,
    total_spend: l2.total_spend,
  }));

  return (
    <Card sx={{ mb: 3, maxWidth: 900, margin: "0 auto" }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          {`${year ? ` ${year}` : ""} Yearly Spend`}
        </Typography>
        <BarChart
          dataset={rows}
          xAxis={[
            {
              dataKey: "level_2",
              label: "Category",
              scaleType: "band",
              groupPadding: 0.3,
              categoryGapRatio: 0.2,
            },
          ]}
          series={[
            {
              dataKey: "total_spend",
              label: "Total Spend (€)",
              color: "#1976d2",
              valueFormatter: (v) => `${v.toFixed(2)} €`,
            },
          ]}
          groupBy="level_1"
          height={400}
          sx={{
            ".MuiChartsAxis-tickLabel": { fontSize: 12 },
            ".MuiChartsLegend-root": { fontSize: 13 },
          }}
          tooltip={{
            formatter: (params) => `${params.value.toFixed(2)} €`,
          }}
        />
      </CardContent>
    </Card>
  );
}
