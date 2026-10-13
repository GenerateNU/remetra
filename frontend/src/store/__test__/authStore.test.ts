import { useAuthStore } from "../useAuthStore";
import { authService } from "../../api/auth_service";
import { clerkSignIn, clerkSignOut, clerkSignUp } from "../../auth/clerkSession";

jest.mock("../../api/auth_service", () => ({
  ...jest.requireActual("../../api/auth_service"),
  authService: {
    getMe: jest.fn(),
    updateProfile: jest.fn(),
  },
}));

jest.mock("../../auth/clerkSession", () => ({
  clerkSignIn: jest.fn(),
  clerkSignUp: jest.fn(),
  clerkSignOut: jest.fn(),
}));

const mockGetMe = authService.getMe as jest.Mock;
const mockClerkSignIn = clerkSignIn as jest.Mock;
const mockClerkSignUp = clerkSignUp as jest.Mock;
const mockClerkSignOut = clerkSignOut as jest.Mock;

const resetStore = () => {
  useAuthStore.getState().clearLocal();
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
    mockClerkSignIn.mockResolvedValue(undefined);
    mockClerkSignUp.mockResolvedValue(undefined);
    mockClerkSignOut.mockResolvedValue(undefined);
    mockGetMe.mockResolvedValue({
      username: "testuser",
      email: "testuser@example.com",
    });
  });

  test("cold start with no stored state", () => {
    const { isAuthenticated, hasCompletedOnboarding } = useAuthStore.getState();

    expect(isAuthenticated).toBe(false);
    expect(hasCompletedOnboarding).toBe(false);
    expect(getInitialScreen()).toBe("auth");
  });

  test("login signs in with Clerk and loads the profile", async () => {
    await useAuthStore.getState().login({
      username: "testuser",
      password: "password123",
    });

    const { isAuthenticated, hasCompletedOnboarding, user } = useAuthStore.getState();

    expect(mockClerkSignIn).toHaveBeenCalledWith("testuser", "password123");
    expect(mockGetMe).toHaveBeenCalledTimes(1);
    expect(isAuthenticated).toBe(true);
    expect(user.name).toBe("testuser");
    expect(user.email).toBe("testuser@example.com");
    expect(hasCompletedOnboarding).toBe(false);
    expect(getInitialScreen()).toBe("onboarding");
  });

  test("login failure does not update state", async () => {
    mockClerkSignIn.mockRejectedValue(new Error("Incorrect username or password"));

    await expect(
      useAuthStore.getState().login({
        username: "bad",
        password: "wrong",
      })
    ).rejects.toThrow("Incorrect username or password");

    expect(useAuthStore.getState().isAuthenticated).toBe(false);
    expect(mockGetMe).not.toHaveBeenCalled();
    expect(getInitialScreen()).toBe("auth");
  });

  test("register signs up with Clerk and loads the profile", async () => {
    await useAuthStore.getState().register({
      username: "newuser",
      email: "new@example.com",
      password: "password123",
    });

    expect(mockClerkSignUp).toHaveBeenCalledWith("newuser", "new@example.com", "password123");
    expect(mockClerkSignIn).not.toHaveBeenCalled();
    expect(mockGetMe).toHaveBeenCalledTimes(1);
    expect(useAuthStore.getState().isAuthenticated).toBe(true);
    expect(useAuthStore.getState().user.email).toBe("testuser@example.com");
    expect(useAuthStore.getState().user.name).toBe("testuser");
  });

  test("register failure does not update state", async () => {
    mockClerkSignUp.mockRejectedValue(new Error("Username already registered"));

    await expect(
      useAuthStore.getState().register({
        username: "existing",
        email: "taken@example.com",
        password: "password123",
      })
    ).rejects.toThrow("Username already registered");

    expect(useAuthStore.getState().isAuthenticated).toBe(false);
  });

  test("logout clears the session and signs out of Clerk", async () => {
    await useAuthStore.getState().login({
      username: "testuser",
      password: "password123",
    });
    useAuthStore.getState().completeOnboarding();

    useAuthStore.getState().logout();

    expect(mockClerkSignOut).toHaveBeenCalled();
    expect(useAuthStore.getState().isAuthenticated).toBe(false);
    expect(useAuthStore.getState().hasCompletedOnboarding).toBe(false);
    expect(useAuthStore.getState().user.email).toBeNull();
    expect(getInitialScreen()).toBe("auth");
  });
});
