import Panel from "../components/panel.jsx";

export default function GameMessage(props) {
  return (
    <Panel
      {...props}
      autoClose={0}
    />
  );
}