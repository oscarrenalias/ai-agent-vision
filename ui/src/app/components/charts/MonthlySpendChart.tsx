import { PieChart } from "@mui/x-charts/PieChart";
import { useItemTooltip } from "@mui/x-charts/ChartsTooltip";
import { useEffect, useState } from "react";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
import IconButton from "@mui/material/IconButton";
import ArrowBackIosNewIcon from "@mui/icons-material/ArrowBackIosNew";
import ArrowForwardIosIcon from "@mui/icons-material/ArrowForwardIos";
import Skeleton from "@mui/material/Skeleton";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";

export function MonthlySpendChart({
  year,
  month,
  setYear,
  setMonth,
}: {
  year: number;
  month: number;
  setYear: (y: number) => void;
  setMonth: (m: number) => void;
}) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    fetch(`/api/analytics/monthly_spend?year=${year}&month=${month}`)
      .then(async (res) => {
        if (!res.ok) {
          throw new Error("Network response was not ok");
        }
        // If response is empty, treat as no data
        const text = await res.text();
        if (!text) {
          return { overall: [], level_1: [], level_2: [] };
        }
        try {
          const d = JSON.parse(text);
          return d.monthly_spend || { overall: [], level_1: [], level_2: [] };
        } catch {
          return { overall: [], level_1: [], level_2: [] };
        }
      })
      .then((monthlySpend) => {
        setData(monthlySpend);
        setLoading(false);
      })
      .catch(() => {
        setError("Failed to load monthly spend data");
        setLoading(false);
      });
  }, [year, month]);

  const handlePrevMonth = () => {
    let newMonth = month - 1;
    let newYear = year;
    if (newMonth < 1) {
      newMonth = 12;
      newYear -= 1;
    }
    setYear(newYear);
    setMonth(newMonth);
  };

  const handleNextMonth = () => {
    let newMonth = month + 1;
    let newYear = year;
    if (newMonth > 12) {
      newMonth = 1;
      newYear += 1;
    }
    setYear(newYear);
    setMonth(newMonth);
  };

  // Only show error if fetch failed, not if data is just empty
  if (error && !data) return <div>{error}</div>;

  let rows: any[] = [];
  if (data && data.level_2 && Array.isArray(data.level_2)) {
    rows = data.level_2.map((l2: any) => ({
      level_1: l2._id?.level_1,
      level_2: l2._id?.level_2,
      total_spend: l2.total_spend,
    }));
  }

  let total = 0;
  if (
    data &&
    data.overall &&
    Array.isArray(data.overall) &&
    data.overall[0]?.total_spend != null
  ) {
    total = data.overall[0].total_spend;
  }

  const monthName = new Date(year, month - 1).toLocaleString("default", {
    month: "long",
  });
  const noData = !rows.length;

  // Prepare a map from level_2 to its level_3 items (use only level_2 as key)
  let level3Map: Record<string, string[]> = {};
  if (data && data.level_3 && Array.isArray(data.level_3)) {
    data.level_3.forEach((l3: any) => {
      const key = l3.level_2;
      if (!level3Map[key]) level3Map[key] = [];
      // Use l3.level_3 or l3.label or l3.name as the display name
      let display = l3.level_3 || l3.label || l3.name || "(unnamed)";
      if (display === null) display = "(none)";
      level3Map[key].push(display);
    });
  }

  let pieData = rows.map((row) => ({
    id: row.level_2,
    value: row.total_spend,
    label: row.level_2,
    level_2: row.level_2,
  }));

  function CustomPieTooltip({
    level3Map,
  }: {
    level3Map: Record<string, string[]>;
  }) {
    const tooltipData = useItemTooltip();
    if (!tooltipData) return null;
    const key = tooltipData.label;
    let l3List = key !== undefined ? level3Map[key] || [] : [];
    // Filter out empty/null values, but if all are empty, show "No breakdown available"
    const hasNonEmpty = l3List.some(
      (v) => v && v !== "(none)" && v !== "(unnamed)"
    );
    if (!hasNonEmpty && l3List.length > 0) l3List = ["No breakdown available"];
    return (
      <Paper
        elevation={0}
        sx={{
          m: 1,
          p: 1.5,
          border: "solid",
          borderWidth: 2,
          borderColor: "divider",
          minWidth: 180,
        }}
      >
        <Stack direction="column" alignItems="flex-start">
          <Stack direction="row" alignItems="center">
            <div
              style={{
                width: 11,
                height: 11,
                borderRadius: "50%",
                backgroundColor: tooltipData.color,
              }}
            />
            <Typography sx={{ ml: 2 }} fontWeight="light">
              {tooltipData.label}
            </Typography>
            <Typography sx={{ ml: 2 }}>{tooltipData.formattedValue}</Typography>
          </Stack>
          {l3List.length > 0 && (
            <div style={{ marginTop: 6 }}>
              <div style={{ fontWeight: 500, marginBottom: 2 }}>
                Level 3 breakdown:
              </div>
              <ul style={{ margin: 0, paddingLeft: 18 }}>
                {l3List.map((name, idx) => (
                  <li key={idx}>{name || "(none)"}</li>
                ))}
              </ul>
            </div>
          )}
        </Stack>
      </Paper>
    );
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
          <IconButton
            onClick={handlePrevMonth}
            size="small"
            aria-label="Previous Month"
            disabled={loading}
          >
            <ArrowBackIosNewIcon fontSize="small" />
          </IconButton>
          <span style={{ margin: "0 8px" }}>
            {monthName} {year} Spend
          </span>
          <IconButton
            onClick={handleNextMonth}
            size="small"
            aria-label="Next Month"
            disabled={loading}
          >
            <ArrowForwardIosIcon fontSize="small" />
          </IconButton>
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
          <div style={{ position: "relative" }}>
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
              hideLegend={true}
            >
              <CustomPieTooltip level3Map={level3Map} />
            </PieChart>
          </div>
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
