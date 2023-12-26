<template>
  <div class="container mt-5">
    <div v-for="(items, tableName) in result" :key="tableName" class="mb-5">
      <!-- Capitalize first letter of each table -->
      <h2>{{ capitalizeFirstLetter(tableName) }}</h2>

      <!-- Template for Tags part of the page with input, button and Existing tags header-->
      <template v-if="tableName === 'tags'">
        <div class="input-group mb-3 mt-3 w-50">
          <input type="text" class="form-control" v-model="tag_value" placeholder="Tag name" />
          <button class="btn btn-primary" @click="createTag">Create new tag</button>
        </div>
        <hr/>
        <h4>Existing tags:</h4>
      </template>

      <!-- Table tags, items are shown horizontally -->
      <ul v-if="tableName === 'tags'" class="horizontal-list">
        <li v-for="item in items" :key="item[0]" class="horizontal-list-item">
          🏷️ {{ item.join('') }}
        </li>
      </ul>

      <!-- Table orders, also displaying tags associated to order and button to add tag to an order -->
      <ul v-else class="list-group">
        <li v-for="item in items" :key="item[0]" class="list-group-item">
            <span v-for="(column, columnIndex) in item" :key="columnIndex" :class="'orders-column'">
                {{ column }}
            </span>
            <button class="btn btn-secondary ml-3" @click="showTagsDropdown(item[0])">+</button>
            <select v-if="item[0] === selectedOrderId" class="form-control mt-2" @change="addTagToOrder($event)">
                <option>Select from existing tags</option>
                <option v-for="tag in tags" :key="tag.id" :value="tag.id">{{ tag.value }}</option>
            </select>
        </li>
    </ul>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  // Prepare data
  data() {
    return {
      result: {},
      tag_value: '',
      selectedOrderId: -1,
      tags: [],
    };
  },
  mounted() {
    // Get the default endpoint
    axios.get('http://localhost:8000/')
      .then(response => {
        this.result = response.data;
      })
      .catch(error => {
        console.error('Error fetching data:', error);
      });
  },
  methods: {
    // Capitalize first letter of each table
    capitalizeFirstLetter(string) {
      return string.charAt(0).toUpperCase() + string.slice(1);
    },
    // Create new tag using the create_tag endpoint
    async createTag() {
      try {
        // Check if the tag name is not empty
        if (!this.tag_value) {
            alert("Tag name cannot be empty!");
            return;
        }
        await fetch(`http://localhost:8000/create_tag/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            tag_value: this.tag_value
          })
        });
        alert("New tag created successfully.");
        // Refresh browser
        window.location.reload();
      } catch (error) {
        console.error('Error inserting value:', error);
        alert('Error creating tag.');
      }
    },
    // Set selectedOrderId, then get tags from BE and show them in the dropdown
    async showTagsDropdown(orderId) {
      this.selectedOrderId = orderId;
      try {
          const response = await axios.get(`http://localhost:8000/tags/`);
          this.tags = response.data.tags;
      } catch (error) {
          console.error('Error fetching tags:', error);
      }
    },
    // Add selected tag to order via associate_tag endpoint
    async addTagToOrder(event) {
      const tagId = parseInt(event.target.value);
      try {
        await fetch(`http://localhost:8000/associate_tag/`, {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json'
          },
          body: JSON.stringify({
              order_id: this.selectedOrderId,
              tag_id: tagId
          })
        });
        alert("Tag added to order successfully.");
        // Refresh browser
        window.location.reload();
      } catch (error) {
        console.error('Error adding tag to order:', error);
        alert('Error adding tag to order.');
      }
    }
  }
};
</script>

<style>
.horizontal-list {
  display: flex;
  flex-wrap: nowrap;
  overflow-x: auto;
  list-style-type: none;
  padding: 0;
}

.horizontal-list-item {
  flex: 0 0 auto;
  padding: 10px;
  border: 1px solid #ccc;
  margin-right: 10px;
}

.orders-column {
  line-height: 38px;
  margin-right: 50px;
}

.orders-column:last-child {
  margin-right: 0;
}

.orders-column:first-child {
  margin-right: 0;
  visibility: hidden;
}

.btn-secondary {
  float: right;
}
</style>