if (typeof global.structuredClone === 'undefined') {
  global.structuredClone = (obj) => JSON.parse(JSON.stringify(obj));
}
global.__ExpoImportMetaRegistry = { register: () => {} };
jest.mock("@react-native-async-storage/async-storage", () =>
  require("@react-native-async-storage/async-storage/jest/async-storage-mock")
);
// react-native-keyboard-controller needs native code; use the mock it ships for Jest
jest.mock("react-native-keyboard-controller", () => require("react-native-keyboard-controller/jest"));
