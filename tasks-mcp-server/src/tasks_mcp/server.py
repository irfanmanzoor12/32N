from mcp.server.fastmcp import FastMCP
from tasks_mcp.tools.add import tasks_add
from tasks_mcp.tools.finish import tasks_finish
from tasks_mcp.tools.cancel import tasks_cancel
from tasks_mcp.tools.defer import tasks_defer
from tasks_mcp.tools.update import tasks_update
from tasks_mcp.tools.get import tasks_get
from tasks_mcp.tools.list import tasks_list
from tasks_mcp.tools.focus import tasks_focus
from tasks_mcp.tools.search import tasks_search

mcp = FastMCP("tasks_mcp", host="127.0.0.1", port=8000, stateless_http=True)

mcp.tool(name="tasks_add",    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})(tasks_add)
mcp.tool(name="tasks_finish", annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True})(tasks_finish)
mcp.tool(name="tasks_cancel", annotations={"readOnlyHint": False, "destructiveHint": True,  "idempotentHint": True})(tasks_cancel)
mcp.tool(name="tasks_defer",  annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})(tasks_defer)
mcp.tool(name="tasks_update", annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})(tasks_update)
mcp.tool(name="tasks_get",    annotations={"readOnlyHint": True,  "destructiveHint": False, "idempotentHint": True})(tasks_get)
mcp.tool(name="tasks_list",   annotations={"readOnlyHint": True,  "destructiveHint": False, "idempotentHint": True})(tasks_list)
mcp.tool(name="tasks_focus",  annotations={"readOnlyHint": True,  "destructiveHint": False, "idempotentHint": True})(tasks_focus)
mcp.tool(name="tasks_search", annotations={"readOnlyHint": True,  "destructiveHint": False, "idempotentHint": True})(tasks_search)

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
