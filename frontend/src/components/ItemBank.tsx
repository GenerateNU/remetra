import { View, Text, TouchableOpacity } from 'react-native';
import { X } from 'lucide-react-native';

interface ItemBankProps {
  title: string;
  subtitle: string;
  items: { name: string, id: string }[];
  emptyMessage: string;
  onRemove: (id: string) => void;
  onAdd: () => void;
}

export function ItemBank({
  title,
  subtitle,
  items,
  emptyMessage,
  onRemove,
  onAdd,
}: ItemBankProps) {
  return (
    <View className="mt-4 mb-8">
      <Text className="text-xl text-remetra-burgundy font-ptserif text-center mb-1 font-normal">
        {title}
      </Text>
      <Text className="text-sm text-remetra-espresso font-ptserif text-center mb-4 opacity-80">
        {subtitle}
      </Text>

      <View className="bg-white/60 border border-remetra-mauve/40 rounded-xl min-h-[120px] p-3">
        <View className="flex-row flex-wrap gap-2">
          {items.map((item) => (
            <View
              key={item.id}
              className="flex-row items-center bg-white border border-remetra-mauve/30 rounded-full px-3 py-2"
            >
              <TouchableOpacity
                onPress={() => onRemove(item.id)}
                hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
                className="mr-2"
              >
                <X size={14} color="#C85A4A" strokeWidth={2.5} />
              </TouchableOpacity>
              <Text className="text-remetra-espresso font-ptserif text-sm">
                {item.name}
              </Text>
            </View>
          ))}

          <TouchableOpacity
            className="flex-row items-center bg-remetra-coral/20 border border-dashed border-remetra-coral/50 rounded-full px-4 py-2"
            onPress={onAdd}
            activeOpacity={0.7}
          >
            <Text className="text-remetra-espresso font-ptserif text-sm font-bold">+ Add</Text>
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
