import { useEffect } from 'react';
import { View, Text, FlatList, Pressable, Switch, ActivityIndicator, StyleSheet } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useChocolates } from './useChocolates';
import { useFilterStore } from './useFilterStore';
import { ChocolateCard } from './ChocolateCard';

export function ChocolatesScreen() {
  const { chocolates, isLoading, error, fetchChocolates } = useChocolates();
  
  const inStockOnly = useFilterStore((s) => s.in_stock_only);
  const setInStockOnly = useFilterStore((s) => s.setInStockOnly);

  useEffect(() => {
    fetchChocolates({ in_stock_only: inStockOnly });
  }, [fetchChocolates, inStockOnly]);

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <Text style={styles.title}>Chocolates</Text>

      <View style={styles.filterRow}>
        <Text style={styles.filterLabel}>In stock only</Text>
        <Switch value={inStockOnly} onValueChange={setInStockOnly} />
      </View>

      {isLoading && <ActivityIndicator size="large" style={styles.loader} />}

      {error && (
        <View style={styles.errorContainer}>
          <Text style={styles.errorText}>{error}</Text>
          <Pressable style={styles.retryButton} onPress={() => fetchChocolates({ in_stock_only: inStockOnly })}>
            <Text style={styles.retryText}>Retry</Text>
          </Pressable>
        </View>
      )}

      {!isLoading && !error && (
        <FlatList
          data={chocolates}
          keyExtractor={(item) => item.id}
          renderItem={({ item }) => <ChocolateCard chocolate={item} />}
          contentContainerStyle={styles.list}
          ListEmptyComponent={<Text style={styles.emptyText}>No chocolates found</Text>}
        />
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F9FAFB' },
  title: { fontSize: 28, fontWeight: '700', paddingHorizontal: 16, paddingTop: 16, paddingBottom: 8 },
  filterRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 16, paddingVertical: 12, backgroundColor: '#fff', marginBottom: 12 },
  filterLabel: { fontSize: 16 },
  loader: { marginTop: 32 },
  errorContainer: { padding: 16, alignItems: 'center' },
  errorText: { color: '#DC2626', marginBottom: 12 },
  retryButton: { backgroundColor: '#4F46E5', paddingHorizontal: 16, paddingVertical: 8, borderRadius: 8 },
  retryText: { color: '#fff', fontWeight: '600' },
  list: { paddingHorizontal: 16 },
  emptyText: { textAlign: 'center', color: '#6B7280', marginTop: 32 },
});
