import { useListOrdersQuery } from "../services/ordersApi";
import { queryErrorText } from "../services/queryError";

export default function OrdersTable() {
  const {
    data: orders = [],
    isFetching,
    isLoading,
    isError,
    error,
    refetch,
  } = useListOrdersQuery();

  if (isLoading) return <div className="card">Loading orders...</div>;

  return (
    <div className="card">
      <h2 className="section-title" style={{ marginTop: 0 }}>
        Orders ({orders.length})
      </h2>
      <button
        onClick={() => refetch()}
        style={{ marginLeft: 12 }}
        disabled={isFetching}
      >
        {isFetching ? "Refreshing…" : "Refresh"}
      </button>
      {error && (
        <div
          className="status-banner"
          style={{ background: "#fbe3e3", color: "#c23636" }}
        >
          {queryErrorText(error, "Failed to load orders.")}
          {orders.length > 0 && " — showing last loaded data."}
        </div>
      )}
      <table className="orders-table" style={{ opacity: isError ? 0.5 : 1 }}>
        <thead>
          <tr>
            <th>Order</th>
            <th>Status</th>
            <th>Total</th>
            <th>Ordered</th>
          </tr>
        </thead>
        <tbody>
          {orders.map((o) => (
            <tr key={o.id}>
              <td>{o.id}</td>
              <td>{o.status}</td>
              <td>
                {o.total_amount.toFixed(2)} {o.currency}
              </td>
              <td>{new Date(o.order_date).toLocaleDateString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
