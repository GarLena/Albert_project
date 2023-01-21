from PyPDF2 import PdfReader
import re
import pandas
import os

directory = "C:/Users/lenka/OneDrive/Plocha/100 days od Python/Projects/Albert projekt/tickets/"

for filename in os.listdir(directory):
    with open(os.path.join(directory,filename), 'rb') as f:
        pdf = PdfReader(f)
        page = pdf.pages[0]
        text = page.extract_text()
        print(filename)


    def shopping_list(ticket):
        """Slicing the shopping list to only get bought items and its price"""
        start_slice = ticket.index("Cena") + 5
        stop_slice = ticket.index("Celkem") - 1
        a = slice(start_slice, stop_slice)
        return ticket[a]


    def date_and_time(ticket):
        """Slicing the shopping list to only get the date and time of the shopping"""
        date_info = slice(ticket.index("Trans")+6, ticket.index("Trans")+22)
        return ticket[date_info]


    lines = shopping_list(text).split("\n")

    """Dividing the lines into a list of bought items and list of its prices"""
    bought_items = [line for line in lines if len(re.sub("[^0-9]", "", line)) <= len(re.sub("[^a-zA-Z]", "", line))
                    and "Kč" not in line]
    items_price = [line for line in lines if len(re.sub("[^0-9]", "", line)) >= len(re.sub("[^a-zA-Z]", "", line))]

    # Removing lines for discounts or credit counts which are not relevant for the analysis
    bought_items = [item for item in bought_items if "kredity" not in item if "Akce" not in item if "SLEVA" not in item]

    items_price_lines = [item for item in items_price if (item.count("Kč") > 1) or ("x" not in item)]
    # for item in items_price:
    #     if item.count("Kč") > 1:
    #         items_price_lines.append(item)
    #     elif item.count("Kč") == 1 and "x" not in item:
    #         items_price_lines.append(item)

    units = [float(item.split(" ", maxsplit=1)[0]) for item in items_price_lines]
    # for item in items_price_lines:
    #     a = item.split(" ", maxsplit=1)
    #     units.append(float(a[0]))

    """Reformation of the prices list into a list of float total prices and into a list of prices per unit"""
    new_total_prices = []
    new_unit_prices = []

    for item in items_price_lines:
        if item.count("Kč") > 1:
            start_index = item.find("č") + 1
            end_index = item.find("K", start_index) - 1
            a = slice(start_index, end_index)
            b = item.find(" ")
            if float(item[0:b]) > 1:
                price_per_unit = round(float(item[a]) / int(item[0]), 1)
                new_unit_prices.append(price_per_unit)
                new_total_prices.append(float(item[a]))
            else:
                new_unit_prices.append(float(item[a]))
                new_total_prices.append(float(item[a]))
        else:
            end_index = item.find("K") - 1
            a = slice(0, end_index)
            item = item[a]
            new_total_prices.append(float(item))
            new_unit_prices.append(float(item))

    shopping_dict = {"Item": bought_items,
                     "Total price": new_total_prices,
                     "Price per unit": new_unit_prices,
                     "Units": units,
                     }


# Kontrolní printy
#     print(len(bought_items))
#     print(len(new_total_prices))
#     print(len(new_unit_prices))
#     print(len(units))

    date_time = date_and_time(text).split(" ")
    date = [int(item[slice(0, 2)]) for item in date_time if ":" not in item]
    time = [item for item in date_time if ":" in item]
    # for item in date_time:
    #     if ":" not in item:
    #         a = slice(0, 2)
    #         date.append(int(item[a]))
    #     else:
    #         time.append(item)

    date_time_dict = {
        "Day": date[0],
        "Month": date[1],
        "Year": date[2],
        "Hour": time
    }

    shopping_data = pandas.DataFrame(shopping_dict)
    shopping_date_time = pandas.DataFrame(date_time_dict)
    new = pandas.concat([shopping_data, shopping_date_time], axis=1)
    new.index += 1

    print(new)

    # Renaming the PDF file and getting the CSV file to have the same name
    old_name = f"./tickets/{filename}"
    new_name = f"./tickets/{date[0]}_{date[1]}_{date[2]}_{time[0][0:2]}h.pdf"
    
    os.rename(old_name, new_name)

    # Creating the CSV file
    new.to_csv(f"{filename[0:12]}.csv")

