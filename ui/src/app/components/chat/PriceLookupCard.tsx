import React from "react";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemText from "@mui/material/ListItemText";

export default function PriceLookupCard({
  items,
  args,
}: {
  items: Array<{ name: string; price: number | string; unit?: string }>;
  args?: any;
}) {
  // Sort items by price (ascending)
  const sortedItems = [...(items || [])].sort((a, b) => {
    const priceA = typeof a.price === "string" ? parseFloat(a.price) : a.price;
    const priceB = typeof b.price === "string" ? parseFloat(b.price) : b.price;
    return priceA - priceB;
  });

  return (
    <Card
      sx={{
        width: "100%",
        maxWidth: 420,
        borderRadius: 3,
        boxShadow: 3,
        position: "relative",
        mb: 2,
        maxHeight: 300,
        display: "flex",
        flexDirection: "column",
      }}
    >
      <CardContent sx={{ pb: 1, pt: 2, px: 2 }}>
        <Typography
          variant="subtitle1"
          className="price-lookup-title"
          gutterBottom
          sx={{ fontWeight: 600, mb: 1, fontSize: 16 }}
        >
          Price Lookup{args?.item ? `: ${args.item}` : ""}
        </Typography>
        <Box sx={{ overflowY: "auto", maxHeight: 180 }}>
          <List dense sx={{ p: 0 }}>
            {sortedItems && sortedItems.length > 0 ? (
              sortedItems.map((item, idx) => (
                <ListItem
                  key={idx}
                  divider
                  sx={{ py: 0.5, px: 1, minHeight: 32 }}
                >
                  <ListItemText
                    primary={
                      <Box
                        sx={{
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center",
                        }}
                      >
                        <span
                          style={{
                            fontSize: 14,
                            marginRight: 12,
                            flex: 1,
                            minWidth: 0,
                            wordBreak: "break-word",
                            whiteSpace: "normal",
                          }}
                          title={item.name}
                        >
                          {item.name}
                        </span>
                        <span
                          style={{
                            fontWeight: 500,
                            fontSize: 14,
                            whiteSpace: "nowrap",
                            marginLeft: 12,
                          }}
                        >
                          {typeof item.price === "number"
                            ? item.price.toFixed(2)
                            : item.price}{" "}
                          €{item.unit ? ` / ${item.unit}` : ""}
                        </span>
                      </Box>
                    }
                  />
                </ListItem>
              ))
            ) : (
              <Typography variant="body2" color="text.secondary">
                No items to display.
              </Typography>
            )}
          </List>
        </Box>
      </CardContent>
    </Card>
  );
}
