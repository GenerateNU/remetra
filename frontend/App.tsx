import { RootNavigator } from './src/navigation/RootNavigator';
import "./global.css";

console.log('App.tsx loaded');

export default function App() {
  console.log('App rendering');
  return <RootNavigator />;
}