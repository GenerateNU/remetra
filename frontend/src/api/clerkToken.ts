type TokenGetter = () => Promise<string | null>;

let tokenGetter: TokenGetter | null = null;

export const setClerkTokenGetter = (getter: TokenGetter | null) => {
  tokenGetter = getter;
};

export const getClerkToken = async (): Promise<string | null> => {
  if (!tokenGetter) return null;
  return tokenGetter();
};
