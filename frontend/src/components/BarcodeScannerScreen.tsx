import { View, Text, TouchableOpacity, StyleSheet } from "react-native";
import { useNavigation, useRoute } from "@react-navigation/native";
import { CameraView, useCameraPermissions } from "expo-camera";
import { useEffect, useState } from "react";

export const BarcodeScannerScreen = () => {
  const navigation = useNavigation<any>();
  const route = useRoute<any>();
  const onScanned = route.params?.onScanned;

  const [permission, requestPermission] = useCameraPermissions();
  const [scanned, setScanned] = useState(false);

  useEffect(() => {
    if (!permission?.granted) requestPermission();
  }, []);

  const handleBarCodeScanned = async ({ data }: { data: string }) => {
    if (scanned) return;
    setScanned(true);

    try {
      const res = await fetch(
        `https://world.openfoodfacts.org/api/v0/product/${data}.json`
      );
      const json = await res.json();
      const product = json.product;

      const name = product?.product_name ?? "Unknown Food";
      const ingredients = product?.ingredients_text
        ? product.ingredients_text.split(",").map((i: string) => i.trim())
        : [];

      onScanned?.({ name, ingredients });
      navigation.goBack();
    } catch (err) {
      console.error("Barcode lookup failed:", err);
      setScanned(false);
    }
  };

  if (!permission?.granted) {
    return (
      <View style={styles.center}>
        <Text style={styles.msg}>Camera access is needed to scan barcodes.</Text>
        <TouchableOpacity style={styles.btn} onPress={requestPermission}>
          <Text style={styles.btnText}>Grant Permission</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={StyleSheet.absoluteFill}>
      <CameraView
        style={StyleSheet.absoluteFill}
        facing="back"
        onBarcodeScanned={handleBarCodeScanned}
        barcodeScannerSettings={{ barcodeTypes: ["ean13", "ean8", "upc_a", "upc_e", "code128"] }}
      />
      <TouchableOpacity
        style={{ position: "absolute", top: 60, left: 20 }}
        onPress={() => navigation.goBack()}
      >
        <Text style={{ color: "white", fontSize: 18 }}>← Cancel</Text>
      </TouchableOpacity>
      <Text style={{ position: "absolute", bottom: 80, alignSelf: "center", color: "white", fontSize: 16 }}>
        Point camera at barcode
      </Text>
    </View>
  );
};

const styles = StyleSheet.create({
  center: { flex: 1, justifyContent: "center", alignItems: "center", padding: 24 },
  msg: { textAlign: "center", marginBottom: 16, color: "#555" },
  btn: { backgroundColor: "#C85A4A", paddingHorizontal: 24, paddingVertical: 12, borderRadius: 20 },
  btnText: { color: "#fff", fontWeight: "600" },
});