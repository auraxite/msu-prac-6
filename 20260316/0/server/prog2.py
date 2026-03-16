import asyncio

async def echo(reader, writer):
    while data := await reader.readline():
        unicode_data = data.decode('utf8')

        if unicode_data.split()[0] == 'print':
            writer.write(' '.join(word for word in unicode_data.split()[1:]).encode('utf-8'))
            writer.write('\n'.encode('utf-8'))
        elif unicode_data.split()[0] == 'info':
            if unicode_data.split()[1] == 'host':
                writer.write((str(writer.get_extra_info('peername')[0]) + '\n').encode('utf-8'))
            elif unicode_data.split()[1] == 'port':
                writer.write((str(writer.get_extra_info('peername')[1]) + '\n').encode('utf-8'))
        else:
            writer.write("UNKNOWN COMMAND".encode('utf-8'))

    writer.close()
    await writer.wait_closed()

async def main():
    server = await asyncio.start_server(echo, '0.0.0.0', 1337)
    async with server:
        await server.serve_forever()

asyncio.run(main())