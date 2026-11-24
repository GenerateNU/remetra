import { fireEvent, render, screen } from '@testing-library/react-native';
import { PasswordInput } from '../PasswordInput';

describe('PasswordInput', () => {
  it('masks the password by default', () => {
    // Arrange / Act
    render(<PasswordInput placeholder="Password" />);

    // Assert
    expect(screen.getByPlaceholderText('Password').props.secureTextEntry).toBe(true);
    expect(screen.getByLabelText('Show password')).toBeTruthy();
  });

  it('reveals the password when the eye button is pressed', () => {
    // Arrange
    render(<PasswordInput placeholder="Password" />);

    // Act
    fireEvent.press(screen.getByLabelText('Show password'));

    // Assert
    expect(screen.getByPlaceholderText('Password').props.secureTextEntry).toBe(false);
    expect(screen.getByLabelText('Hide password')).toBeTruthy();
  });

  it('masks the password again on a second press', () => {
    // Arrange
    render(<PasswordInput placeholder="Password" />);
    fireEvent.press(screen.getByLabelText('Show password'));

    // Act
    fireEvent.press(screen.getByLabelText('Hide password'));

    // Assert
    expect(screen.getByPlaceholderText('Password').props.secureTextEntry).toBe(true);
    expect(screen.getByLabelText('Show password')).toBeTruthy();
  });

  it('keeps the typed value when toggling visibility', () => {
    // Arrange
    render(<PasswordInput placeholder="Password" value="hunter22" onChangeText={() => {}} />);

    // Act
    fireEvent.press(screen.getByLabelText('Show password'));

    // Assert
    expect(screen.getByPlaceholderText('Password').props.value).toBe('hunter22');
  });

  it('forwards onChangeText to the underlying input', () => {
    // Arrange
    const onChangeText = jest.fn();
    render(<PasswordInput placeholder="Password" onChangeText={onChangeText} />);

    // Act
    fireEvent.changeText(screen.getByPlaceholderText('Password'), 'secret123');

    // Assert
    expect(onChangeText).toHaveBeenCalledWith('secret123');
  });

  it('disables autocorrect and autocapitalize so visible passwords are not altered', () => {
    // Arrange / Act
    render(<PasswordInput placeholder="Password" />);
    const input = screen.getByPlaceholderText('Password');

    // Assert
    expect(input.props.autoCorrect).toBe(false);
    expect(input.props.autoCapitalize).toBe('none');
  });
});
