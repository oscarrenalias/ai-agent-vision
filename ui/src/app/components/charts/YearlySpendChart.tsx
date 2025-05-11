import { PieChart } from "@mui/x-charts/PieChart";
import { useEffect, useState } from "react";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
import Skeleton from "@mui/material/Skeleton";

export function YearlySpendChart() {
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

  if (error && !data) return <div>{error}</div>;

  let rows: any[] = [];
  if (data && data.level_2 && Array.isArray(data.level_2)) {
    rows = data.level_2.map((l2: any) => ({
      level_1: l2.level_1,
      level_2: l2.level_2,
      total_spend: l2.total_spend,
    }));
  }

  const year =
    data && data.overall && data.overall[0]?._id?.year
      ? data.overall[0]._id.year
      : "";
  const noData = !rows.length;

  let total = 0;
  if (
    data &&
    data.overall &&
    Array.isArray(data.overall) &&
    data.overall[0]?.total_spend != null
  ) {
    total = data.overall[0].total_spend;
  }

  let pieData = rows.map((row) => ({
    id: row.level_2,
    value: row.total_spend,
    label: row.level_2,
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
          {`${year ? ` ${year}` : ""} Yearly Spend`}
        </Typography>
        <Typography variant="subtitle1" align="center" sx={{ mb: 1 }}>
          Total: {total.toFixed(2)} €
        </Typography>
        {loading ? (
          <Skeleton
            variant="rectangular"
            height={260}
            sx={{ borderRadius: 2, mb: 2 }}
          />
        ) : (
          <PieChart
            series={[
              {
                data: pieData,
                innerRadius: 60,
                outerRadius: 120,
                paddingAngle: 2,
                arcLabel: (item) => `${item.value.toFixed(2)} €`,
                arcLabelMinAngle: 15, // Hide labels for small arcs
              },
            ]}
            height={260}
            legend={{ position: "right" }}
          />
        )}
        {!loading && noData && (
          <Typography
            variant="body2"
            color="text.secondary"
            align="center"
            sx={{ mt: 2 }}
          ></Typography>
        )}
      </CardContent>
    </Card>
  );
}
