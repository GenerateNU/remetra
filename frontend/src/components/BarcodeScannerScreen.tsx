import { View, Text, TouchableOpacity, TextInput } from "react-native";
import { useNavigation, useRoute } from "@react-navigation/native";
import { CameraView, useCameraPermissions } from "expo-camera";
import { useState, useRef } from "react";
import { useBankStore } from "../store/bankStore";

export const BarcodeScannerScreen = () => {
  const navigation = useNavigation<any>();
  const { setScannedFood } = useBankStore();
  const [permission, requestPermission] = useCameraPermissions();
  const [scanned, setScanned] = useState(false);
  const scannedRef = useRef(false);

  const handleBarCodeScanned = async ({ data }: { data: string }) => {
    if (scannedRef.current) return;
    scannedRef.current = true;
    setScanned(true); 

    try {
      const res = await fetch(
        `https://world.openfoodfacts.org/api/v0/product/${data}.json`
      );

      if (!res.ok) {
        console.error('API error:', res.status);
        scannedRef.current = false;
        setScanned(false);
        return;
      }

      const json = await res.json();
      const product = json.product;

      if (!product) {
        scannedRef.current = false;
        setScanned(false);
        return;
      }

      const name = product.product_name ?? "Unknown";

      const skipPatterns = [
        /^made of/i,
        /^less than/i,
        /^contains/i,
        /^to maintain/i,
      ];


      const ingredients = product.ingredients
      ? product.ingredients
          .filter((i: any) => 
            i.rank !== undefined && 
            i.percent_estimate > 2 &&
            !skipPatterns.some(p => p.test(i.text))
          )
          .map((i: any) => i.text?.toLowerCase().trim())
          .filter(Boolean)
      : [];

        setScannedFood({ name, ingredients });
        navigation.goBack();
      } catch (err) {
        console.error("Barcode lookup failed:", err);
        scannedRef.current = false;
        setScanned(false);
      }
    };
  if (!permission?.granted) {
    return (
      <View style={styles.container}>
        <View style={styles.permissionContent}>
          <Text style={styles.text}>Camera permission is required.</Text>
          <TouchableOpacity style={styles.btn} onPress={requestPermission}>
            <Text style={styles.btnText}>Grant Permission</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  }


  return (
    <View style={styles.container}>
      <CameraView
        style={StyleSheet.absoluteFillObject}
        facing="back"
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
  permissionContent: { flex: 1, justifyContent: "center", alignItems: "center", paddingHorizontal: 32 },
  overlay: { position: "absolute", bottom: 60, width: "100%", alignItems: "center", gap: 12 },
  instructions: { color: "#fff", fontSize: 16, marginBottom: 8 },
  cancelBtn: { paddingVertical: 10, paddingHorizontal: 20 },
  cancelText: { color: "#eea487", fontSize: 16 },
  btn: { backgroundColor: "#C85A4A", borderRadius: 25, paddingVertical: 14, paddingHorizontal: 32 },
  btnText: { color: "#fff", fontSize: 16, fontWeight: "600" },
  text: { color: "#fff", fontSize: 16, marginBottom: 20 },
});
