import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
);

export default function StatsChart({ title, data }) {
  if (!data?.length) {
    return null;
  }

  const labels = data.map(
    (item) => item.category || item.priority || item.status || item.label,
  );
  const values = data.map((item) => item.count || item.value);

  return (
    <div className="chart-card">
      {title && <h3>{title}</h3>}
      <Bar
        data={{
          labels,
          datasets: [
            { label: "Count", data: values, backgroundColor: "#4f46e5" },
          ],
        }}
        options={{ responsive: true, plugins: { legend: { display: false } } }}
      />
    </div>
  );
}
