import { View, Text, TouchableOpacity } from 'react-native';

interface ItemBankProps {
  title: string;
  subtitle: string;
  description: string;
  items: { name: string }[];
  emptyMessage: string;
  onRemove: (name: string) => void;
  onAdd: () => void;
}

export function ItemBank({
  title,
  subtitle,
  description,
  items,
  emptyMessage,
  onRemove,
  onAdd,
}: ItemBankProps) {
  return (
    <View className="mb-8">
      <Text className="text-xl text-remetra-rose font-ptserif text-center mb-1 font-normal">
        {title}
      </Text>
      <Text className="text-sm text-remetra-rose font-ptserif text-center mb-1 opacity-80">
        {subtitle}
      </Text>
      <Text className="text-xs text-remetra-mauve font-ptserif text-center mb-4">
        {description}
      </Text>

      <View className="bg-white/60 border border-remetra-mauve/40 rounded-xl min-h-[120px] p-3">
        <View className="flex-row flex-wrap gap-2">
          {items.map((item) => (
            <View
              key={item.name}
              className="flex-row items-center bg-white border border-remetra-mauve/30 rounded-full px-3 py-2"
            >
              <TouchableOpacity
                onPress={() => onRemove(item.name)}
                hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
              >
                <Text className="text-remetra-rose text-sm mr-2 font-bold">✕</Text>
              </TouchableOpacity>
              <Text className="text-remetra-burgundy font-ptserif text-sm">
                {item.name}
              </Text>
            </View>
          ))}

          <TouchableOpacity
            className="flex-row items-center bg-remetra-coral/20 border border-dashed border-remetra-coral/50 rounded-full px-4 py-2"
            onPress={onAdd}
            activeOpacity={0.7}
          >
            <Text className="text-remetra-coral font-ptserif text-sm font-bold">+ Add</Text>
          </TouchableOpacity>
        </View>

        {items.length === 0 && (
          <View className="items-center justify-center py-4">
            <Text className="text-remetra-mauve font-ptserif text-sm italic">
              {emptyMessage}
            </Text>
          </View>
        )}
      </View>
    </View>
  );
}
