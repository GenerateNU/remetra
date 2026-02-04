import { View, Text, StyleSheet } from 'react-native';
import type { Chocolate } from './chocolates';

interface ChocolateCardProps {
  chocolate: Chocolate;
}

export function ChocolateCard({ chocolate }: ChocolateCardProps) {
  return (
    <View style={styles.card}>
      <View style={styles.header}>
        <Text style={styles.name}>{chocolate.name}</Text>
        <View style={[styles.badge, chocolate.stock_quantity > 0 ? styles.inStock : styles.outOfStock]}>
          <Text style={styles.badgeText}>{chocolate.stock_quantity > 0 ? 'In Stock' : 'Out of Stock'}</Text>
        </View>
      </View>
      {chocolate.description && (
        <Text style={styles.description}>{chocolate.description}</Text>
      )}
      <Text style={styles.price}>${Number(chocolate.price).toFixed(2)}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: { backgroundColor: '#fff', padding: 16, borderRadius: 12, marginBottom: 12, shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.1, shadowRadius: 4, elevation: 3 },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 },
  name: { fontSize: 18, fontWeight: '600', flex: 1 },
  badge: { paddingHorizontal: 8, paddingVertical: 4, borderRadius: 4 },
  inStock: { backgroundColor: '#D1FAE5' },
  outOfStock: { backgroundColor: '#FEE2E2' },
  badgeText: { fontSize: 12, fontWeight: '500' },
  description: { color: '#6B7280', marginBottom: 8 },
  price: { fontSize: 20, fontWeight: '700', color: '#4F46E5' },
});