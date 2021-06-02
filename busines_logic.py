import aiofiles
import asyncio


async def serve_client(reader, writer):
    '''The function reads data, processes requests, and sends a response to the client'''
    request = await read_request(reader)
    response = await handle_request(request)
    await send_response(writer, response)

async def read_request(reader) -> str:
    request = b""
    while True:
        data = await reader.read(1024)
        if not data: break
        request += data
        return request.decode('UTF-8')

async def handle_request(request: str) -> bytes:
    if request == None:
        response = "НИПОНЯЛ РКСОК/1.0"
        return response.encode('UTF-8')
    name = determine_name(request)
    standart = determine_standart(request)
    if len(name) > 30 or not request.endswith("\r\n\r\n") or standart != "РКСОК/1.0":
        response = "НИПОНЯЛ РКСОК/1.0"
        return response.encode('UTF-8')
    method = determine_method(request)
    if method == "ЗОПИШИ":
        response_from_authorities = await ask_permission(request)
        if response_from_authorities != "possible":
            return response_from_authorities.encode('UTF-8')
        await write_down_phone(request)
        response = 'НОРМАЛДЫКС РКСОК/1.0'
        return response.encode('UTF-8')
    elif method == "ОТДОВАЙ":
        response_from_authorities = await ask_permission(request)
        if response_from_authorities != "possible":
            return response_from_authorities.encode('UTF-8')
        response = await get_phone(request)
        return response.encode('UTF-8')
    elif method == "УДОЛИ":
        response_from_authorities = await ask_permission(request)
        if response_from_authorities != "possible":
            return response_from_authorities.encode('UTF-8')
        response = await delete_phone(request)
        return response.encode('UTF-8')
    else:
        response = "НИПОНЯЛ РКСОК/1.0"
        return response.encode('UTF-8')

async def send_response(writer, response):
    writer.write(response)
    await writer.drain()
    writer.close()

def determine_standart(request: str) -> str:
    standart = request.split('\r\n')[0].split(' ')[-1]
    return standart

def determine_method(data: str) -> str:
    method = data.split('\r\n')[0].split(' ')[0]
    return method

def determine_name(data: str) -> str:
    name = " ".join(data.split('\r\n')[0].split()[1:-1])
    return name

def determine_phone(data: str) -> list:
    phones = []
    strings = data.split('\r\n')[1:]
    for string in strings:
        if string != "":
            phones.append(string)
    return phones

async def write_down_phone(data: str) -> None:
    name = determine_name(data)
    phones = determine_phone(data)
    new_entry = f"{name}"
    for phone in phones:
        new_entry += f"!!!{phone}"
    new_entry += "\n"
    async with aiofiles.open("phonebook.txt", mode='r') as f:
        phonebook = await f.readlines()
    for index, value in enumerate(phonebook):
        if value == "":
            del phonebook[index]
        elif value.split("!!!")[0] == name:
            del phonebook[index]
    phonebook.append(new_entry)
    async with aiofiles.open("phonebook.txt", mode='w') as f:
        await f.writelines(phonebook)

async def get_phone(data: str) -> str:
    name = determine_name(data)
    async with aiofiles.open("phonebook.txt", mode='r') as f:
        phonebook = await f.readlines()
    if phonebook == []:
        answer = "НИНАШОЛ РКСОК/1.0"
        return answer
    for line in phonebook:
        if line.split("!!!")[0] == name:
            phones = "\r\n".join(line.split("!!!")[1:])
            answer = "НОРМАЛДЫКС РКСОК/1.0\r\n" + phones
            return answer
        else:
            answer = "НИНАШОЛ РКСОК/1.0"
            return answer

async def delete_phone(data: str) -> str:
    name = determine_name(data)
    async with aiofiles.open("phonebook.txt", mode='r') as f:
        phonebook = await f.readlines()
    if phonebook == []:
        answer = "НИНАШОЛ РКСОК/1.0"
        return answer
    answer = ""
    for index, value in enumerate(phonebook):
        if value == "":
            del phonebook[index]
        elif value.split("!!!")[0] == name:
            answer += "НОРМАЛДЫКС РКСОК/1.0"
            del phonebook[index]
    async with aiofiles.open("phonebook.txt", mode='w') as f:
        await f.writelines(phonebook)
    if answer == "":
        message = "НИНАШОЛ РКСОК/1.0"
        return message
    else:
        return answer

async def ask_permission(data: str, host: str = "vragi-vezde.to.digital", port: int = 51624) -> str:
    '''Sending a request to the verification server'''
    reader, writer = await asyncio.open_connection(host, port)
    request_body = f"АМОЖНА? РКСОК/1.0\r\n+{data}".encode("UTF-8")
    writer.write(request_body)
    await writer.drain()
    response = await reader.read(1024)
    writer.close()
    await writer.wait_closed()
    response_decoded = response.decode("UTF-8")
    yes_or_no = determine_yes_or_no(response_decoded)
    return yes_or_no

def determine_yes_or_no(response_body: str) -> str:
    yes_or_no = response_body.split('\r\n')[0].split(' ')[0]
    answer = ""
    if yes_or_no == "МОЖНА":
        answer += "possible"
        return answer
    else:
        return response_body
