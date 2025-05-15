import numpy as np


def get_preview(photo_field):
    """
    Extracts the URL from the 'large' thumbnail in a photo field structure.
    """
    if not isinstance(photo_field, list) or not photo_field:
        return None

    first_item = photo_field[0]

    if not isinstance(first_item, dict):
        return None

    thumbnails = first_item.get('thumbnails')
    if isinstance(thumbnails, dict) and 'large' in thumbnails:
        large_thumbnail_info = thumbnails['large']
        url = large_thumbnail_info['url']
        return url

    # Return None if the expected structure or URL is not found
    return None


def is_valid_number(number):
    """
    Checks if the input is a valid number (not None, NaN).

    Args:
        number: The input to validate.

    Returns:
        bool: True if the number is valid, False otherwise.
    """
    return number is not None and not (
            (isinstance(number, str)) or
            (hasattr(number, "dtype") and np.isnan(number)) or
            (isinstance(number, float) and np.isnan(number))
    )


def format_as_percent(number, default="N/A", decimal_places=2):
    """
    Formats a number as a percentage where 0.1 becomes "10.0%"

    Args:
        number: The number to format (int, float, np.float64, or other numpy numeric types)
        default: The value to return if number is None or np.nan (default: "0.0%")
        decimal_places: Number of decimal places to display (default: 1)

    Returns:
        str: The formatted percentage
    """
    # Check if the number is valid
    if not is_valid_number(number):
        return default

    # Convert numpy types to Python float
    if hasattr(number, "dtype"):
        number = float(number)

    # Multiply by 100 to convert decimal to percentage
    percentage = number * 100

    # Format with the specified number of decimal places
    format_str = "{:." + str(decimal_places) + "f}%"
    formatted = format_str.format(percentage)

    return formatted


def format_as_dollars(number, default="N/A"):
    """
    Formats a number as a dollar amount with the format "$ X,XXX.XX"

    Args:
        number: The number to format (int, float, np.float64, or other numpy numeric types)
        default: The value to return if number is None or np.nan (default: "$ 0.00")

    Returns:
        str: The formatted dollar amount
    """
    # Check if the number is valid
    if not is_valid_number(number):
        return default

    number = float(number)

    # Format the number with commas and two decimal places
    formatted = "${:,.2f}".format(float(number))
    # Add space after dollar sign for the requested format
    # formatted = formatted.replace("$", "$ ")

    return formatted


def format_metric_badge(percentage_change, period="1mo"):
    """
    Format a percentage change for display in a badge with appropriate styling.
    
    Args:
        percentage_change: The percentage change value (can be positive or negative)
        period: The time period for the change (e.g., "1mo", "90 days")
        
    Returns:
        tuple: (text, color) where text is the formatted badge text and color is 'red' or 'green'
    """
    if not is_valid_number(percentage_change):
        return None, None
    
    # Determine if it's a positive or negative change
    is_positive = percentage_change > 0
    
    # Format the percentage with the appropriate sign
    if is_positive:
        text = f"+{percentage_change:.0f}%"
        color = "green"
    else:
        text = f"{percentage_change:.0f}%"
        color = "red"
        
    # Add the period in parentheses
    text = f"{text} ({period})"
    
    return text, color
