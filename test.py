import hashlib
import aiohttp

async def uploadImage(file):
    url = "https://filesoss.yunzuoye.net/XHFileServer/file/upload/CA107011/"
    headers = {
        "XueHai-MD5": hashlib.md5(await file.read()).hexdigest()
    }
    data = aiohttp.FormData()
    data.add_field('files', await file.read(), filename=file.filename)
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=data, ssl=False, timeout=30) as response:
            return (await response.json())["uploadFileDTO"]["fileId"]

if __name__ == '__main__':
    import asyncio
    filepath = "./exampleImg/ikun.jpg"
    async def main():
        with open(filepath, 'rb') as f:
            fileId = await uploadImage(f)
            print(fileId)
    asyncio.run(main())