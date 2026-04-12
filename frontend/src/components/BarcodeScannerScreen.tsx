import { View, Text, TouchableOpacity, TextInput } from "react-native";
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
    <View className="flex-1 p-6 pt-[60px] bg-white">
      <TouchableOpacity onPress={() => navigation.goBack()}>
        <Text className="text-base text-remetra-accent mb-6">← Cancel</Text>
      </TouchableOpacity>

      <Text className="text-[22px] font-semibold text-remetra-accent mb-5">
        Test Barcode Lookup
      </Text>

      <TextInput
        className="border border-remetra-border rounded-lg p-3 mb-3 text-base"
        placeholder="Enter barcode number..."
        value={barcode}
        onChangeText={setBarcode}
        keyboardType="numeric"
      />

      <TouchableOpacity
        className="bg-remetra-rose rounded-full py-3.5 items-center"
        onPress={handleLookup}
      >
        <Text className="text-white text-base font-semibold">
          {loading ? "Looking up..." : "Look Up"}
        </Text>
      </TouchableOpacity>

      {result && (
        <Text className="mt-6 text-sm text-neutral-600 leading-[22px]">{result}</Text>
      )}
    </View>
  );
};
