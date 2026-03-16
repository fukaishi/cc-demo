"use client";

import { useState, useEffect, useCallback } from "react";
import styles from "./page.module.css";

const API_URL = "http://localhost:8000";

type Todo = {
  id: number;
  title: string;
  completed: boolean;
};

type Filter = "all" | "active" | "completed";

export default function Home() {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [newTitle, setNewTitle] = useState("");
  const [filter, setFilter] = useState<Filter>("all");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTodos = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/todos`);
      if (!res.ok) throw new Error("Failed to fetch todos");
      const data = await res.json();
      setTodos(data);
      setError(null);
    } catch {
      setError("Failed to load todos. Is the backend running?");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTodos();
  }, [fetchTodos]);

  const filteredTodos = todos.filter((todo) => {
    if (filter === "active") return !todo.completed;
    if (filter === "completed") return todo.completed;
    return true;
  });

  const activeCount = todos.filter((todo) => !todo.completed).length;
  const completedCount = todos.filter((todo) => todo.completed).length;

  const addTodo = async (e: React.FormEvent) => {
    e.preventDefault();
    const title = newTitle.trim();
    if (!title) return;

    try {
      const res = await fetch(`${API_URL}/todos`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title }),
      });
      if (!res.ok) throw new Error("Failed to add todo");
      setNewTitle("");
      setError(null);
      await fetchTodos();
    } catch {
      setError("Failed to add todo.");
    }
  };

  const toggleTodo = async (id: number) => {
    try {
      const res = await fetch(`${API_URL}/todos/${id}`, {
        method: "PATCH",
      });
      if (!res.ok) throw new Error("Failed to toggle todo");
      setError(null);
      await fetchTodos();
    } catch {
      setError("Failed to update todo.");
    }
  };

  const deleteTodo = async (id: number) => {
    try {
      const res = await fetch(`${API_URL}/todos/${id}`, {
        method: "DELETE",
      });
      if (!res.ok) throw new Error("Failed to delete todo");
      setError(null);
      await fetchTodos();
    } catch {
      setError("Failed to delete todo.");
    }
  };

  const clearCompleted = async () => {
    try {
      const completedTodos = todos.filter((todo) => todo.completed);
      await Promise.all(
        completedTodos.map((todo) =>
          fetch(`${API_URL}/todos/${todo.id}`, { method: "DELETE" })
        )
      );
      setError(null);
      await fetchTodos();
    } catch {
      setError("Failed to clear completed todos.");
    }
  };

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Todo App</h1>

      {error && <div className={styles.error}>{error}</div>}

      <form className={styles.form} onSubmit={addTodo}>
        <input
          className={styles.input}
          type="text"
          placeholder="What needs to be done?"
          value={newTitle}
          onChange={(e) => setNewTitle(e.target.value)}
        />
        <button
          className={styles.addButton}
          type="submit"
          disabled={!newTitle.trim()}
        >
          Add
        </button>
      </form>

      <div className={styles.filters}>
        {(["all", "active", "completed"] as Filter[]).map((f) => (
          <button
            key={f}
            className={`${styles.filterButton} ${
              filter === f ? styles.filterButtonActive : ""
            }`}
            onClick={() => setFilter(f)}
          >
            {f.charAt(0).toUpperCase() + f.slice(1)}
          </button>
        ))}
      </div>

      {loading ? (
        <div className={styles.loading}>Loading...</div>
      ) : filteredTodos.length === 0 ? (
        <div className={styles.empty}>
          {filter === "all"
            ? "No todos yet. Add one above!"
            : `No ${filter} todos.`}
        </div>
      ) : (
        <ul className={styles.list}>
          {filteredTodos.map((todo) => (
            <li key={todo.id} className={styles.todoItem}>
              <div
                className={`${styles.checkbox} ${
                  todo.completed ? styles.checkboxChecked : ""
                }`}
                onClick={() => toggleTodo(todo.id)}
                role="checkbox"
                aria-checked={todo.completed}
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    toggleTodo(todo.id);
                  }
                }}
              >
                {todo.completed && <span className={styles.checkmark}>&#10003;</span>}
              </div>
              <span
                className={`${styles.todoTitle} ${
                  todo.completed ? styles.todoTitleCompleted : ""
                }`}
                onClick={() => toggleTodo(todo.id)}
              >
                {todo.title}
              </span>
              <button
                className={styles.deleteButton}
                onClick={() => deleteTodo(todo.id)}
                aria-label={`Delete ${todo.title}`}
              >
                &#10005;
              </button>
            </li>
          ))}
        </ul>
      )}

      {todos.length > 0 && (
        <div className={styles.footer}>
          <span className={styles.itemCount}>
            {activeCount} {activeCount === 1 ? "item" : "items"} left
          </span>
          {completedCount > 0 && (
            <button className={styles.clearButton} onClick={clearCompleted}>
              Clear completed
            </button>
          )}
        </div>
      )}
    </div>
  );
}
