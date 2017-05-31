import matplotlib.pyplot as plt
import sys


def get_data_from_file(filename):
    try:
        with open(filename, 'r') as f:
            return f.readlines()[:-1]
    except IOError:
        print("Given filename doesn't exist!")
        sys.exit()
        
def filter_row(row, is_last=False):
    if is_last:
        return row[9:-9]
    return row[9:-3]
        
def data_list_to_string(data):
    first, *inside, last = data
    inside = ''.join(map(filter_row, inside))
    return ''.join((filter_row(first), inside, filter_row(last, is_last=True)))
    
def process_text(data):
    prepared_to_conversion_data = slice_string_data(
        data_list_to_string(data)
    )
    return list(map(string_to_humidity_temp_height, 
                    prepared_to_conversion_data))
    
    
def slice_string_data(data, size=6):
    for idx in range(0, len(data) - (len(data) % size), size):
        row = data[idx: idx + size]
        # End of measurements (maybe baloon has crashed)
        if row == '000000':
            break
        yield row
        
def string_to_humidity_temp_height(data):
    temp = int(data[:2], 16)
    humidity = int(data[2:4], 16)
    height = int(data[4:], 16) * 10
    return (temp, humidity, height)


def plot_data(temp, humidity, height):
    f, (ax1, ax2, ax3) = plt.subplots(
        3, 1, 
        figsize=(10, 15),
    )
    time = list(range(0, 10 * len(temp), 10))
    ax1.plot(time, temp, label='Temperatura', color='red')
    ax1.set_title('Temperatura')
    ax1.set_ylabel('st. [C]')
    ax1.set_xlabel('Czas [s]')
    ax2.plot(time, humidity, label='Wilgotnosc', color='blue')
    ax2.set_title('Wilgotnosc')
    ax2.set_ylabel('[%]')
    ax2.set_xlabel('Czas [s]')
    ax3.plot(time, height, label='Height', color='orange')
    ax3.set_title('Wysokosc')
    ax3.set_xlabel('Czas [s]')
    ax3.set_ylabel('[m] n.p.m.')
    f.subplots_adjust(hspace=0.3)
    plt.show()
    
def plot_from_file(filename):
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
