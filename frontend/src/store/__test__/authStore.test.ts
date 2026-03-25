import { useAuthStore } from "../useAuthStore";
import { authService } from "../../api/auth_service";

// Mock the entire auth service module
jest.mock("../../api/auth_service", () => ({
  ...jest.requireActual("../../api/auth_service"),
  authService: {
    login: jest.fn(),
    register: jest.fn(),
    getMe: jest.fn(),
  },
}));

const mockLogin = authService.login as jest.Mock;
const mockRegister = authService.register as jest.Mock;
const mockGetMe = authService.getMe as jest.Mock;

const resetStore = () => {
  useAuthStore.getState().logout();
  useAuthStore.setState({ hasCompletedOnboarding: false });
};

const getInitialScreen = () => {
  const { isAuthenticated, hasCompletedOnboarding } = useAuthStore.getState();
  if (!isAuthenticated) return "auth";
  if (!hasCompletedOnboarding) return "onboarding";
  return "main";
};

describe("AuthStore navigation states", () => {
  beforeEach(() => {
    resetStore();
    jest.clearAllMocks();

    // Default mock: successful login
    mockLogin.mockResolvedValue({
      access_token: "valid-token-123",
      token_type: "bearer",
      username: "testuser",
    });

    // Default mock: successful registration
    mockRegister.mockResolvedValue(undefined);

    // Default mock: successful getMe
    mockGetMe.mockResolvedValue({
      username: "testuser",
      email: "testuser@example.com",
    });
  });

  test("cold start with no stored state", () => {
    const { isAuthenticated, accessToken, hasCompletedOnboarding } =
      useAuthStore.getState();

    expect(isAuthenticated).toBe(false);
    expect(accessToken).toBeNull();
    expect(hasCompletedOnboarding).toBe(false);
    expect(getInitialScreen()).toBe("auth");
  });

  test("login sets auth state and fetches profile on success", async () => {
    await useAuthStore.getState().login({
      username: "testuser",
      password: "password123",
    });

    const { isAuthenticated, accessToken, hasCompletedOnboarding, user } =
      useAuthStore.getState();

    expect(mockLogin).toHaveBeenCalledWith({
      username: "testuser",
      password: "password123",
    });
    expect(mockGetMe).toHaveBeenCalledTimes(1);
    expect(isAuthenticated).toBe(true);
    expect(accessToken).toBe("valid-token-123");
    expect(user.name).toBe("testuser");
    expect(user.email).toBe("testuser@example.com");
    expect(hasCompletedOnboarding).toBe(false);
    expect(getInitialScreen()).toBe("onboarding");
  });

  test("login failure does not update state", async () => {
    mockLogin.mockRejectedValue(new Error("Invalid credentials"));

    await expect(
      useAuthStore.getState().login({
        username: "bad",
        password: "wrong",
      })
    ).rejects.toThrow("Invalid credentials");

    expect(useAuthStore.getState().isAuthenticated).toBe(false);
    expect(useAuthStore.getState().accessToken).toBeNull();
    expect(getInitialScreen()).toBe("auth");
  });

  test("register calls signup then auto-logs in (no extra getMe call)", async () => {
    await useAuthStore.getState().register({
      username: "newuser",
      email: "new@example.com",
      password: "password123",
    });

    expect(mockRegister).toHaveBeenCalledWith({
      username: "newuser",
      email: "new@example.com",
      password: "password123",
    });
    // register chains directly into login (not via store.login, so getMe is not called)
    expect(mockLogin).toHaveBeenCalledWith({
      username: "newuser",
      password: "password123",
    });
    expect(mockGetMe).not.toHaveBeenCalled();
    expect(useAuthStore.getState().isAuthenticated).toBe(true);
    expect(useAuthStore.getState().accessToken).toBe("valid-token-123");
    expect(useAuthStore.getState().user.email).toBe("new@example.com");
  });

  test("register failure does not update state", async () => {
    mockRegister.mockRejectedValue(new Error("Email already exists"));

    await expect(
      useAuthStore.getState().register({
        username: "existing",
        email: "taken@example.com",
        password: "password123",
      })
    ).rejects.toThrow("Email already exists");

    expect(mockLogin).not.toHaveBeenCalled();
    expect(useAuthStore.getState().isAuthenticated).toBe(false);
  });

  test("full flow: login, complete onboarding, reach main", async () => {
    await useAuthStore.getState().login({
      username: "testuser",
      password: "password123",
    });
    useAuthStore.getState().completeOnboarding();

    expect(useAuthStore.getState().isAuthenticated).toBe(true);
    expect(useAuthStore.getState().accessToken).toBe("valid-token-123");
    expect(useAuthStore.getState().hasCompletedOnboarding).toBe(true);
    expect(getInitialScreen()).toBe("main");
  });

  test("logout clears auth state but not onboarding flag", async () => {
    await useAuthStore.getState().login({
      username: "testuser",
      password: "password123",
    });
    useAuthStore.getState().completeOnboarding();
    useAuthStore.getState().logout();

    const { isAuthenticated, accessToken, hasCompletedOnboarding, user } =
      useAuthStore.getState();

    expect(isAuthenticated).toBe(false);
    expect(accessToken).toBeNull();
    // hasCompletedOnboarding is intentionally preserved so re-login skips onboarding
    expect(hasCompletedOnboarding).toBe(true);
    expect(user).toEqual({
      id: null,
      email: null,
      name: null,
      avatarUrl: null,
    });
    // isAuthenticated=false always lands on auth stack regardless of onboarding flag
    expect(getInitialScreen()).toBe("auth");
  });

  test("re-login after logout skips onboarding when already completed", async () => {
    await useAuthStore.getState().login({ username: "testuser", password: "password123" });
    useAuthStore.getState().completeOnboarding();
    useAuthStore.getState().logout();

    jest.clearAllMocks();
    mockLogin.mockResolvedValue({ access_token: "new-token", token_type: "bearer", username: "testuser" });
    mockGetMe.mockResolvedValue({ username: "testuser", email: "testuser@example.com" });

    await useAuthStore.getState().login({ username: "testuser", password: "password123" });

    expect(getInitialScreen()).toBe("main");
  });
});
