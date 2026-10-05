import { getClerkInstance } from '@clerk/expo';
import { ApiError } from '../api/client';

type ClerkFailure = {
  code?: string;
  message?: string;
  longMessage?: string;
};

function futureSignIn() {
  const future = getClerkInstance().client?.signIn?.__internal_future;
  if (!future) {
    throw new ApiError('Something went wrong. Please try again.');
  }
  return future;
}

function futureSignUp() {
  const future = getClerkInstance().client?.signUp?.__internal_future;
  if (!future) {
    throw new ApiError('Something went wrong. Please try again.');
  }
  return future;
}

function messageFor(error: ClerkFailure, flow: 'sign-in' | 'sign-up'): string {
  const code = error.code ?? '';
  const detail = `${error.longMessage ?? ''} ${error.message ?? ''}`.toLowerCase();

  if (flow === 'sign-in') {
    return 'Incorrect username or password';
  }

  if (code.includes('exist') || detail.includes('exist') || detail.includes('taken')) {
    return 'Username already registered';
  }

  return error.longMessage || error.message || 'Something went wrong. Please try again.';
}

export async function clerkSignIn(username: string, password: string): Promise<void> {
  const signIn = futureSignIn();
  await signIn.reset();

  const { error } = await signIn.password({ identifier: username, password });
  if (error) {
    throw new ApiError(messageFor(error, 'sign-in'));
  }
  if (signIn.status !== 'complete') {
    throw new ApiError('Incorrect username or password');
  }

  const finalized = await signIn.finalize();
  if (finalized.error) {
    throw new ApiError(messageFor(finalized.error, 'sign-in'));
  }
}

export async function clerkSignUp(username: string, email: string, password: string): Promise<void> {
  const signUp = futureSignUp();
  await signUp.reset();

  const { error } = await signUp.password({
    emailAddress: email,
    username,
    password,
  });
  if (error) {
    throw new ApiError(messageFor(error, 'sign-up'));
  }
  if (signUp.status !== 'complete') {
    throw new ApiError('Something went wrong. Please try again.');
  }

  const finalized = await signUp.finalize();
  if (finalized.error) {
    throw new ApiError(messageFor(finalized.error, 'sign-up'));
  }
}

export async function clerkSignOut(): Promise<void> {
  await getClerkInstance().signOut();
}
