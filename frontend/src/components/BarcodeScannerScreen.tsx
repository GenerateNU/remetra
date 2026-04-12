import { View, Text, TouchableOpacity, TextInput } from "react-native";
import { useNavigation, useRoute } from "@react-navigation/native";
import { CameraView, useCameraPermissions } from "expo-camera";
import { useState } from "react";
import { useBankStore } from "../store/bankStore";

export const BarcodeScannerScreen = () => {
  const navigation = useNavigation<any>();
  const { setScannedFood } = useBankStore();
  const [permission, requestPermission] = useCameraPermissions();
  const [scanned, setScanned] = useState(false);

  const handleBarCodeScanned = async ({ data }: { data: string }) => {
    if (scanned) return;
    setScanned(true);

    try {
      const res = await fetch(
        `https://world.openfoodfacts.org/api/v0/product/${data}.json`
      );
      const json = await res.json();
      const product = json.product;

      if (!product) {
        setScanned(false);
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
      console.error("Barcode lookup failed:", err);
      setScanned(false);
    }
  };

  if (!permission?.granted) {
    return (
      <View style={styles.container}>
        <Text style={styles.text}>Camera permission is required.</Text>
        <TouchableOpacity style={styles.btn} onPress={requestPermission}>
          <Text style={styles.btnText}>Grant Permission</Text>
        </TouchableOpacity>
      </View>
    );
  }


  return (
    <View style={styles.container}>
      <CameraView
        style={StyleSheet.absoluteFillObject}
        facing="front"
        onBarcodeScanned={handleBarCodeScanned}
        barcodeScannerSettings={{ barcodeTypes: ["ean13", "ean8", "upc_a", "upc_e"] }}
      />
      <View style={styles.overlay}>
        <Text style={styles.instructions}>Point at a barcode</Text>
        <TouchableOpacity style={styles.cancelBtn} onPress={() => navigation.goBack()}>
          <Text style={styles.cancelText}>← Cancel</Text>
        </TouchableOpacity>
        {scanned && (
          <TouchableOpacity style={styles.btn} onPress={() => setScanned(false)}>
            <Text style={styles.btnText}>Scan Again</Text>
          </TouchableOpacity>
        )}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#000" },
  overlay: { position: "absolute", bottom: 60, width: "100%", alignItems: "center", gap: 12 },
  instructions: { color: "#fff", fontSize: 16, marginBottom: 8 },
  cancelBtn: { paddingVertical: 10, paddingHorizontal: 20 },
  cancelText: { color: "#eea487", fontSize: 16 },
  btn: { backgroundColor: "#C85A4A", borderRadius: 25, paddingVertical: 14, paddingHorizontal: 32 },
  btnText: { color: "#fff", fontSize: 16, fontWeight: "600" },
  text: { color: "#fff", fontSize: 16, marginBottom: 20 },
});
