import matplotlib.pyplot as plt
import sys

# Timedelta between single measurment
TIMEDELTA = 10
# How many first chars we need to drop from each line
DROP_FIRST_N_CHAR = 9
# How many last chars we need to drop from each line
DROP_LAST_N_CHAR = 2
# Size of a single block 2x bit for temp, height, humidity
DATA_CHUNK = 6

def get_data_from_file(filename):
    '''
    Args:
        :filename: :str: File name with measurment data

    Out:
        :list: List of all but last line from file.
    '''
    try:
        with open(filename, 'r') as f:
            return f.readlines()[:-1]
    except IOError:
        print("Given filename doesn't exist!")
        sys.exit()
        
def filter_row(row, is_last=False):
    '''
    Args:
        :row: :str: Single line of data
        :is_last: :bool: True if it's the last one else False 
    Out:
        :str: String with data stripped of unnecesary gibberish chars
    '''
    if is_last:
        return row[DROP_FIRST_N_CHAR:-DROP_FIRST_N_CHAR]
    return row[DROP_FIRST_N_CHAR:-(DROP_LAST_N_CHAR + 1)]
        
def data_list_to_string(data):
    '''
    Args:
        :data: :list: List of raw lines with data
    Out:
        :str: String of data, stripped of unnecesary chars 
              from front and end of the line.    
    '''
    first, *inside, last = data
    inside = ''.join(map(filter_row, inside))
    return ''.join((filter_row(first), inside, filter_row(last, is_last=True)))
    
def process_text(data):
    '''
    Args:
        :data: :str: Clear string of data without gibberish chars
    Our:
        :list: List of tuples (temp, humidity, height)
    '''
    prepared_to_conversion_data = slice_string_data(
        data_list_to_string(data), size=DATA_CHUNK
    )
    return list(map(string_to_humidity_temp_height, 
                    prepared_to_conversion_data))
    
    
def slice_string_data(data, size):
    '''
    Args:
        :data: :str: String of clean data 
        :size: :int: Length of single block of data 
                     (6 by default due to 2 bits for (temp, height, humidity))
    Out:
        :str: Stream of string blocks of size-length each 
    '''
    for idx in range(0, len(data) - (len(data) % size), size):
        row = data[idx: idx + size]
        # End of measurements (maybe baloon has crashed)
        if row == '000000':
            break
        yield row
        
def string_to_humidity_temp_height(data):
    '''
    Args:
        :data: :str: Single block of data 
    Out:
        :tuple: Tuple of numbers formatted from hexadecimal string to decimal int.
    '''
    temp = int(data[:2], 16)
    humidity = int(data[2:4], 16)
    height = int(data[4:], 16) * 10
    return (temp, humidity, height)


def plot_data(temp, humidity, height):
    ''' 
    Args:
        :temp: :tuple: Tuple of temperatures measurments
        :humidity: :tuple: Tuple of humidity measurments
        :height: :tuple: Tuple of heights measurments
    Out:
        :None: Show a plot based on given data.
    '''
    f, (ax1, ax2, ax3) = plt.subplots(
        3, 1, 
        figsize=(10, 15),
    )
    axis = (ax1, ax2, ax3)
    time = list(range(0, TIMEDELTA * len(temp), TIMEDELTA))
    data = (temp, humidity, height)
    color = ('red', 'blue', 'orange')
    title = ('Temperatura', 'Wilgotnosc', 'Wysokosc')
    y_label = ('st. [C]', '[%]', '[m] n. p. m.')
    x_label = 'Czas [s]'
    xlim = [0, None]
    for ax, data, title, ylabel, color in zip(axis, data, title, y_label, color):
        ax.plot(time, data, color=color)
        ax.set_title(title)
        ax.set_ylabel(ylabel)
        ax.set_xlabel(x_label)
        ax.set_xlim(xlim)
    f.subplots_adjust(hspace=0.3)
    
    plt.show()
    
def plot_from_file(filename):
    '''
    Args:
        :filename: :str: File name
    Out:
        :None: Main function. Take filename, process its data 
               and plot it on a nice-formatted chart.
    '''
    txt = get_data_from_file(filename)
    data = process_text(txt)
    temp, humidity, height = list(zip(*data))
    plot_data(temp, humidity, height)
    
if __name__ == '__main__':
    try:
        filename = sys.argv[1]
    except IndexError:
        print('Filename/path required as argument!')
    else:
        if not filename.endswith('.eep'):
            filename += '.eep'
        plot_from_file(filename)
