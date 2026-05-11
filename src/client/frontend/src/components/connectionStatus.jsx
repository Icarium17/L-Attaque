
export default function ConnectionStatus({ pingMs }) {
  if (!pingMs) return null;
  
  const color = pingMs < 100 ? "text-green-400" 
              : pingMs < 300 ? "text-yellow-400" 
              : "text-red-400";

  return (
    <div className={`text-xl ${color}`}>
      ping: {pingMs}ms
    </div>
  );
}