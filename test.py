import asyncio

# cancel task test
async def test_task():
    print("Task 開始")
    try:
        while True:
            print("Task 運行中...")
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        print("Task 被取消")
    finally:
        print("Task 清理資源完成")

async def main():
    print("測試開始")
    task = asyncio.create_task(test_task())
    await asyncio.sleep(5)
    print("取消任務")
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        print("主程式捕捉到任務取消異常")
    await asyncio.sleep(1)
    print("測試結束")
    
if __name__ == "__main__":
    asyncio.run(main())