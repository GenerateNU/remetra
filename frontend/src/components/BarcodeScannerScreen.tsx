import { View, Text, TouchableOpacity, StyleSheet, TextInput } from "react-native";
import { useNavigation, useRoute } from "@react-navigation/native";
import { useState } from "react";
import { useBankStore } from "../store/bankStore";

export const BarcodeScannerScreen = () => {
  const navigation = useNavigation<any>();
  const route = useRoute<any>();
  const onScanned = route.params?.onScanned;

  const [barcode, setBarcode] = useState("");
  const [result, setResult] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const { setScannedFood } = useBankStore();


  const handleLookup = async () => {
    if (!barcode.trim()) return;
    setLoading(true);
    setResult(null);

    try {
      const res = await fetch(
        `https://world.openfoodfacts.org/api/v0/product/${barcode}.json`
      );
      const json = await res.json();
      const product = json.product;

      if (!product) {
        setResult("Product not found");
        return;
      }

      const name = product.product_name ?? "Unknown";
      const ingredients = product.ingredients
        ? product.ingredients.map((i: any) => 
            i.id.replace(/^en:/, '').replace(/-/g, ' ')
            ).filter(Boolean)
        : [];


      setScannedFood({ name, ingredients });
      navigation.navigate('Summary');
    } catch (err) {
      setResult("Lookup failed");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <TouchableOpacity onPress={() => navigation.goBack()}>
        <Text style={styles.back}>← Cancel</Text>
      </TouchableOpacity>

      <Text style={styles.title}>Test Barcode Lookup</Text>

      <TextInput
        style={styles.input}
        placeholder="Enter barcode number..."
        value={barcode}
        onChangeText={setBarcode}
        keyboardType="numeric"
      />

      <TouchableOpacity style={styles.btn} onPress={handleLookup}>
        <Text style={styles.btnText}>{loading ? "Looking up..." : "Look Up"}</Text>
      </TouchableOpacity>

      {result && (
        <Text style={styles.result}>{result}</Text>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, padding: 24, paddingTop: 60, backgroundColor: '#fff' },
  back: { color: '#eea487', fontSize: 16, marginBottom: 24 },
  title: { fontSize: 22, fontWeight: '600', color: '#eea487', marginBottom: 20 },
  input: { borderWidth: 1, borderColor: '#ccc', borderRadius: 8, padding: 12, marginBottom: 12, fontSize: 16 },
  btn: { backgroundColor: '#C85A4A', borderRadius: 25, paddingVertical: 14, alignItems: 'center' },
  btnText: { color: '#fff', fontSize: 16, fontWeight: '600' },
  result: { marginTop: 24, fontSize: 14, color: '#333', lineHeight: 22 },
});